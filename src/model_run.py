"""Performs model training, generates predictions, and evaluates model."""
import sys
import logging
import warnings
from datetime import datetime
import yaml
import pandas as pd
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
from src.helper_months import date_range_hours
from src.helper_db import add_to_database
from src.helper_s3 import upload_to_s3, download_csv_s3

# Logging
logger = logging.getLogger(__name__)


def model_fun(dataframe, start_date_args, end_date_args, model_params, optional_fit_args):
    """
    Trains a ARIMA model for forecasting inventory for each Citi Bike station
        that has the necessary data
    Args:
        dataframe (pandas DataFrame): input data consisting of confirmed cases globally by day
        start_date_args (dict): ARIMA model required fit parameters
        end_date_args (dict): ARIMA model required fit parameters
        model_params (dict): ARIMA model required fit parameters
        optional_fit_args (dict): ARIMA model additional hyperparameters
    Returns:
        station_models_df (pandas: ARIMA trained model object
    """

    df_loop = dataframe[['station_id', 'date', 'stock']]

    # get list of each station in the dataset
    station_list = dataframe.station_id.unique()

    # initial lists to be appended to through training loop
    mapes_station_arima = []
    stations_w_models = []
    date_time_list = []
    dict_list = []

    # Generate forecast time range (default is until August 4 at midnight)
    start_date = datetime(**start_date_args)
    end_date = datetime(**end_date_args)
    for single_date in date_range_hours(start_date, end_date):
        date_time_list.append(single_date.strftime("%Y-%m-%d %H:%M"))

    # for each station in the list, attempt to build an ARIMA model for forecasting
    warnings.simplefilter('ignore', ConvergenceWarning)
    logger.warning('Running ARIMA model; many station-level outcomes may result in '
                   '"The problem is unconstrained" output.')
    for station in station_list:

        # subset dataframe to station of interest
        df_train = df_loop.loc[dataframe['station_id'] == station]
        df_train.reset_index(inplace=True, drop=True)
        y_var = df_train['stock']

        # only perform training if there are at least 336 hours (2 weeks) of data
        # with at least 1 bike in that station
        enough_data_flag = len(df_train.loc[df_train['stock'] > 0])
        if enough_data_flag > 336:

            # train on all the data
            arima_def = ARIMA(y_var, order=(model_params['p'],
                                            model_params['d'],
                                            model_params['q']))
            model_arima = arima_def.fit(**optional_fit_args)

            # append model object reference to a list
            stations_w_models.append(station)

            # for a rough evaluation of each model, train on all but last 12
            # hours and evaluate on those
            y_train = y_var.iloc[0:len(y_var) - 12]
            y_test = y_var.iloc[-12:]
            arima_model_eval = ARIMA(y_train, order=(model_params['p'],
                                                     model_params['d'],
                                                     model_params['q']))
            model_eval_arima_fit = arima_model_eval.fit(**optional_fit_args)

            y_pred = model_eval_arima_fit.forecast(len(y_test))[0]
            mape_result = (abs((y_pred - y_test) / y_test) * 100).mean()

            # To deal with sparse data and to avoid inf results,
            # cap MAPE upper bound at 100%
            if mape_result > 100:
                mape_val = 100
            else:
                mape_val = mape_result

            mapes_station_arima.append(mape_val)

            # Build forecast table
            forecasts = pd.DataFrame(model_arima.forecast(
                steps=len(date_time_list))).transpose()[0]

            for i in range(0, len(date_time_list)):
                forecast_d = {'station_id': station,
                              'date_time': date_time_list[i],
                              'pred_num_bikes': round(forecasts[i])}
                dict_list.append(forecast_d)

        else:
            pass

    # Create a dataframe of predictions by station, date, and hour
    try:
        predictions = pd.DataFrame(dict_list)
        predictions['date_time'] = pd.to_datetime(predictions['date_time'])
        predictions['date'] = predictions['date_time'].dt.date
        predictions['hour'] = predictions['date_time'].dt.hour
        predictions_output = predictions[['station_id', 'date', 'hour',
                                          'pred_num_bikes']]
    except ValueError as val_e:
        logging.error('ARIMA model structure formatted incorrectly. '
                      'Check values of stations included.')
        logging.error(val_e)
        sys.exit(1)

    # Create a dataframe of MAPE by station
    try:
        station_mapes_df = pd.DataFrame({'Station': stations_w_models,
                                         'MAPE': mapes_station_arima})
        no_model_stations = len(station_list) - len(station_mapes_df)
        logger.info("Station models trained. Models could not be generated"
                    " for %s stations "
                    "due to lack of data.", no_model_stations)
    except TypeError as type_e:
        logging.warning('Stations unable to run, check for -Inf MAPE '
                        'values and try again.')
        logging.warning(type_e)
        sys.exit(1)

    return predictions_output, station_mapes_df


def run_train_models(args):
    """
    Wrapper function to run model traning and evaluation steps
    Args:
        args: From argparse:
           - config (str): Path to yaml file containing relevant
                configurations
           - engine_string (str): sqlalchemy engine string
           - s3_bucket (str): String indicating name of S3 bucket
    Returns:
        None -- wrapper function
    """
    try:
        with open(args.config, "r") as fil:
            config = yaml.load(fil, Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify "
                     "correct filename/path.")
        sys.exit(1)

    # get station level data, train station forecasting models
    logger.info('Reading in time series "bike_stock" data from S3 '
                'at %s...', args.s3_bucket)
    bike_stock_data = download_csv_s3(s3_bucket_name=args.s3_bucket,
                                      bucket_dir_path=config['download_csv_s3']
                                      ['bike_stock_data']['bucket_dir_path'],
                                      input_filename=config['download_csv_s3']
                                      ['bike_stock_data']['input_filename'],
                                      output_filename=config['download_csv_s3']
                                      ['bike_stock_data']['output_filename'])

    logger.info("Training models for each station, this will take"
                " a few moments.")
    logger.warning("You may see some warnings issued from the ARIMA"
                   " fit. Due to the nature of the data for some "
                   "stations, the fit/optimization algorithm encounters"
                   " issues.")
    predictions, station_mapes = model_fun(dataframe=bike_stock_data,
                                           start_date_args=config['forecast_date_range']
                                           ['start_date'],
                                           end_date_args=config['forecast_date_range']
                                           ['end_date'],
                                           model_params=config['arima_params'],
                                           optional_fit_args=config['arima_fit_params'])

    # Append station-level characteristics to predictions table
    logger.info('Reading in stations data from S3 at %s...', args.s3_bucket)
    stations_data = download_csv_s3(s3_bucket_name=args.s3_bucket,
                                    bucket_dir_path=config['download_csv_s3']
                                    ['stations_data']['bucket_dir_path'],
                                    input_filename=config['download_csv_s3']
                                    ['stations_data']['input_filename'],
                                    output_filename=config['download_csv_s3']
                                    ['stations_data']['output_filename'])

    # Merge predictions and stations data
    prediction_df = pd.merge(predictions, stations_data, how='left')
    prediction_df = prediction_df[['station_id', 'name',
                                   'latitude', 'longitude',
                                   'date', 'hour', 'pred_num_bikes']]. \
        sort_values(['longitude', 'latitude'], ascending=(True, False))

    # Save predictions to local file
    prediction_df.to_csv(config['model_run']['prediction_path'], index=False)
    logger.info('Success! Added predictions data locally to: '
                '"%s"', config['model_run']['prediction_path'])

    # Save station-level MAPE to local file
    station_mapes.to_csv(config['model_run']['mape_path'], index=False)
    logger.info('Success! Added predictions evaluation data '
                'locally to: "%s"', config['model_run']['mape_path'])

    # Save predictions and performance metrics to S3
    upload_to_s3(file_local_path=config['model_run']['prediction_path'],
                 s3_bucket=args.s3_bucket,
                 s3_directory=config['model_run']['bucket_dir_path'])
    upload_to_s3(file_local_path=config['model_run']['mape_path'],
                 s3_bucket=args.s3_bucket,
                 s3_directory=config['model_run']['bucket_dir_path'])
    logger.info('Success! Added predictions and performance '
                'metrics data to the "%s" S3 bucket in the "%s" folder.',
                args.s3_bucket, config['model_run']['bucket_dir_path'])

    # Save predictions to Database
    logger.info('Writing predictions data to database at %s.',
                args.engine_string)
    add_to_database(prediction_df, "predictions", 'replace',
                    args.engine_string)
    logger.info('Success! Added predictions data to the database'
                ' at "%s"', args.engine_string)

    # Report average MAPE
    logger.info('Average MAPE across all stations: %s',
                str(station_mapes.MAPE.mean()))
