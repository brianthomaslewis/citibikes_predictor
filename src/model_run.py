import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from sklearn.model_selection import TimeSeriesSplit
import argparse
import yaml
import logging.config
import sys
from datetime import datetime
import os
from helper_months import date_range
from helper_db import get_engine, add_to_database, get_data_from_database
from helper_s3 import upload_to_s3
import config as connection_config

# Logging
# logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)


def read_data_from_db(table, engine_string=None):
    """
    Retrieve data from MySQL database locally or in RDS
    Args:
        table (str): table from which to query database
        engine_string (str): sqlalchemy string for the connection.
    Returns:
        df (pandas DataFrame): DataFrame of covid19 data retrieved from MySQL database
    """

    # get sqlalchemy engine
    engine = get_engine(engine_string)

    # query the database
    query = f"""SELECT * FROM {table} 
--     LIMIT 10000
    """
    df = get_data_from_database(query, engine_string)

    return df


def model_fun(df, start_date_args, end_date_args, model_params, optional_fit_args):
    """
    Trains a ARIMA model for forecasting inventory for each Citi Bike station that has the necessary data
    Args:
        df (pandas DataFrame): input data consisting of confirmed cases globally by day
        start_date_args (dict): ARIMA model required fit parameters
        end_date_args (dict): ARIMA model required fit parameters
        model_params (dict): ARIMA model required fit parameters
        optional_fit_args (dict): ARIMA model additional hyperparameters
    Returns:
        station_models_df (pandas: ARIMA trained model object
    """

    df_loop = df[['station_id', 'date', 'stock']]

    # get list of each station in the dataset
    station_list = df.station_id.unique()

    # initial lists to be appended to through training loop
    mapes_station_arima = []
    stations_w_models = []
    date_time_list = []
    dict_list = []

    # Generate forecast time range (default is until August 4 at midnight)
    start_date = datetime(**start_date_args)
    end_date = datetime(**end_date_args)
    for single_date in date_range(start_date, end_date):
        date_time_list.append(single_date.strftime("%Y-%m-%d %H:%M"))

    # for each station in the list, attempt to build an ARIMA model for forecasting
    warnings.filterwarnings("ignore")  # specify to try to ignore warning messages from ARIMA models
    warnings.simplefilter('ignore', ConvergenceWarning)
    for station in station_list:

        # subset dataframe to station of interest
        df_train = df_loop.loc[df['station_id'] == station]
        df_train.reset_index(inplace=True, drop=True)
        y = df_train['stock']

        # only perform training if there are at least 336 hours (2 weeks) of data with at least 1 bike in that station
        enough_data_flag = len(df_train.loc[df_train['stock'] > 0])
        if enough_data_flag > 336:

            # train on all the data
            arima_def = ARIMA(y, order=(model_params['p'], model_params['d'], model_params['q']))
            model_arima = arima_def.fit(**optional_fit_args)

            # append model object reference to a list
            stations_w_models.append(station)

            # for a rough evaluation of each model, train on all but last 12 hours and evaluate on those
            y_train = y.iloc[0:len(y) - 12]
            y_test = y.iloc[-12:]
            arima_model_eval = ARIMA(y_train, order=(model_params['p'], model_params['d'], model_params['q']))
            model_eval_arima_fit = arima_model_eval.fit(**optional_fit_args)

            y_pred = model_eval_arima_fit.forecast(len(y_test))[0]
            mape_result = (abs((y_pred - y_test) / y_test) * 100).mean()

            # To deal with sparse data and to avoid inf results, cap MAPE upper bound at 100%
            if mape_result > 100:
                mape_result = 100
            else:
                mape_result = mape_result

            mapes_station_arima.append(mape_result)

            # Build forecast table
            forecasts = pd.DataFrame(model_arima.forecast(steps=len(date_time_list))).transpose()[0]

            for i in range(0, len(date_time_list)):
                forecast_d = {'station_id': station,
                              'date_time': date_time_list[i],
                              'pred_num_bikes': round(forecasts[i])}
                dict_list.append(forecast_d)

        else:
            pass

    # Create a dataframe of predictions by station, date, and hour
    predictions = pd.DataFrame(dict_list)
    predictions['date_time'] = pd.to_datetime(predictions['date_time'])
    predictions['date'] = predictions['date_time'].dt.date
    predictions['hour'] = predictions['date_time'].dt.hour
    predictions_output = predictions[['station_id', 'date', 'hour', 'pred_num_bikes']]

    # Create a dataframe of MAPE by station
    station_mapes_df = pd.DataFrame({'Station': stations_w_models, 'MAPE': mapes_station_arima})
    no_model_stations = len(station_list) - len(station_mapes_df)
    logger.info("Station models trained. Models could not be generated for %s stations "
                "due to lack of data.", no_model_stations)

    return predictions_output, station_mapes_df


def run_train_models(args):
    """
    Wrapper function to run model traning and evaluation steps
    Args:
        args: From argparse:
           - config (str): Path to yaml file containing relevant configurations
           - engine_string (str): sqlalchemy engine string
           - s3_bucket (str): String indicating name of S3 bucket
    Returns:
        None -- wrapper function
    """
    try:
        with open(args.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")
        sys.exit(1)

    # get station level data, train station forecasting models
    station_data = read_data_from_db('bike_stock', args.engine_string)
    logger.info("Training models for each station, this will take a few moments.")
    logger.warning("You may see some warnings issued from the ARIMA fit. Due to the nature of the data for some "
                   "stations, the fit/optimization algorithm encounters issues.")
    predictions, station_mapes = model_fun(df=station_data,
                                           start_date_args=config['forecast_date_range']['start_date'],
                                           end_date_args=config['forecast_date_range']['end_date'],
                                           model_params=config['arima_params'],
                                           optional_fit_args=config['arima_fit_params'])

    # Append station-level characteristics to predictions table
    stations_data = read_data_from_db('stations', args.engine_string)
    prediction_df = pd.merge(predictions, stations_data, how='left')
    prediction_df = prediction_df[['station_id', 'name', 'latitude', 'longitude', 'date', 'hour', 'pred_num_bikes']]. \
        sort_values(['longitude', 'latitude'], ascending=(True, False))

    # Save predictions and station-level MAPE to local file
    prediction_df.to_csv(config['model_run']['prediction_path'], index=False)
    logger.info('Success! Added predictions data locally to: "%s"', config['model_run']['prediction_path'])

    station_mapes.to_csv(config['model_run']['mape_path'], index=False)
    logger.info('Success! Added predictions data locally to: "%s"', config['model_run']['mape_path'])

    # Save predictions to S3
    upload_to_s3(file_local_path=config['model_run']['prediction_path'],
                 s3_bucket=args.s3_bucket,
                 s3_directory=config['model_run']['bucket_dir_path'])
    logger.info('Success! Added predictions data to the "%s" S3 bucket in the "%s" folder.',
                args.s3_bucket, config['model_run']['bucket_dir_path'])

    # Save predictions to Database
    logger.info('Writing predictions data to database.')
    add_to_database(prediction_df, "predictions", 'replace', args.engine_string)
    logger.info('Success! Added predictions data to the database at "%s"', args.engine_string)

    # Report average MAPE
    logger.info('Average MAPE across all stations: %s', str(station_mapes.MAPE.mean()))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train time-series forecasting model(s) for stock numbers')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=connection_config.SQLALCHEMY_DATABASE_URI,
                        help="Manually specified engine location.")
    parser.add_argument("--s3_bucket", default=connection_config.S3_BUCKET, help="s3 bucket name")
    arguments = parser.parse_args()
    run_train_models(arguments)

    logger.info("model_run.py was run successfully.")
