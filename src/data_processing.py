import sys
import logging
import yaml
import argparse
import pandas as pd
import numpy as np
from src.helper_db import add_to_database
from src.helper_s3 import download_csv_s3, upload_to_s3

# Logging
logger = logging.getLogger(__name__)

"""Functions to process bike data and shape it for modeling"""


def process_bike_data(trips_df, stations_df, rebalancing_prop):
    """
    Filters raw data to columns of interest and joins trips and stations datasets
    Args:
        trips_df (pandas DataFrame): DataFrame consisting of the trips data acquired from Citi Bike
        stations_df (pandas DataFrame): DataFrame consisting of the stations data acquired from Citi Bike
        rebalancing_prop (double): Proportion from 0-1 to indicate how much daily rebalancing occurs at stations
    Returns:
        df (pandas DataFrame): Reduced columns version of the input DataFrame
    """
    try:
        # Join data
        bikes = pd.merge(trips_df, stations_df,
                         how='left',
                         left_on=['station_id'],
                         right_on=['station_id']). \
            sort_values(['station_id', 'date', 'hour']). \
            drop(['num_bikes_available', 'last_reported'], axis=1)

        # Fill in station-level data and mathematical operations for all observations
        bikes['name'] = bikes.groupby('station_id')['name'].transform(lambda x: x.ffill().bfill())
        bikes['latitude'] = bikes.groupby('station_id')['latitude'].transform(lambda x: x.ffill().bfill())
        bikes['longitude'] = bikes.groupby('station_id')['longitude'].transform(lambda x: x.ffill().bfill())
        bikes['capacity'] = bikes.groupby('station_id')['capacity'].transform(lambda x: x.ffill().bfill())
        bikes['net_flows'] = bikes['outflows'] - bikes['inflows']

        # Calculate stock of bikes, using `rebalancing_prop`
        bikes['stock'] = np.where(
            bikes.groupby(['station_id', 'date'])['hour'].transform('min') == bikes['hour'],
            round(bikes.capacity * rebalancing_prop),
            bikes.net_flows.shift()
        )

        # Create daily running stock
        bikes['stock'] = bikes.groupby(['station_id', 'date'])['stock'].cumsum()
        bikes['date'] = pd.to_datetime(bikes.date)
        bikes['date'] += pd.to_timedelta(bikes.hour, unit='h')

        # Remove unnecessary columns and drop rows with missing values
        bikes_df = bikes.drop(['capacity', 'inflows', 'hour', 'outflows', 'net_flows'], axis=1).dropna()

    except AttributeError:
        logger.error(
            "Your input to the function 'process_bike_data' was not a DataFrame and thus the function could not run")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error in the function 'process_bike_data': %s:%s", type(e).__name__, e)
        sys.exit(1)

    return bikes_df


def run_data_processing(arguments):
    """
    Wrapper function that processes and runs ARIMA on the raw data to obtain results for database upload
    Args:
        arguments: From argparse:
           config (str): Path to yaml file with containing relevant configurations
           engine_string (str): sqlalchemy engine string
           local_flag (bool): the flag used to determine if the scripts will read/write via s3 or local
           s3_bucket (str): name of the S3 bucket to pull data from
    Returns:
        None -- this a wrapper function for the data preparation steps
    """
    try:
        with open(arguments.config, "r") as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")
        sys.exit(1)

    # If --local flag activated, download from local
    if arguments.local_flag:
        trips = pd.read_csv(config['fetch_local_data']['trips_data_path'])
        logger.info('Successfully retrieved trips data from local at "%s"',
                    config['fetch_local_data']['trips_data_path'])
        stations = pd.read_csv(config['fetch_local_data']['stations_data_path'])
        logger.info('Successfully retrieved stations data from local at "%s"',
                    config['fetch_local_data']['stations_data_path'])

    # Otherwise, open up from local
    else:
        logger.info('Retrieving data from S3 at %s', arguments.s3_bucket)
        trips = download_csv_s3(s3_bucket_name=arguments.s3_bucket,
                                bucket_dir_path=config['download_csv_s3']['trips_data']['bucket_dir_path'],
                                input_filename=config['download_csv_s3']['trips_data']['input_filename'],
                                output_filename=config['download_csv_s3']['trips_data']['output_filename'])
        stations = download_csv_s3(s3_bucket_name=arguments.s3_bucket,
                                   bucket_dir_path=config['download_csv_s3']['stations_data']['bucket_dir_path'],
                                   input_filename=config['download_csv_s3']['stations_data']['input_filename'],
                                   output_filename=config['download_csv_s3']['stations_data']['output_filename'])

    # Begin processing bike data
    logger.info('Processing trips and stations data for modeling...')
    bike_df = process_bike_data(trips, stations, config['process_bike_data']['rebalancing_proportion'])

    # Save bike_stock data locally
    bike_df.to_csv(config['process_bike_data']['output_file'], index=False)
    logger.info('Success! Added bike_stock data locally to: "%s"', config['process_bike_data']['output_file'])

    # Save bike_stock data to S3
    upload_to_s3(file_local_path=config['process_bike_data']['output_file'],
                 s3_bucket=arguments.s3_bucket,
                 s3_directory=config['upload_to_s3']['s3_directory'])
    logger.info('Success! Added bike_stock data to the "%s" folder in the "%s" S3 bucket .',
                config['upload_to_s3']['s3_directory'], arguments.s3_bucket)

    # Save bike_stock data to database
    try:
        logger.info('Attempting to add bike stock data to database at %s...', arguments.engine_string)
        add_to_database(bike_df, "bike_stock", 'replace', arguments.engine_string)
        logger.info('Success! Added data to "bike_stock" table at the following engine_string: %s',
                    arguments.engine_string)
        logger.info("data_processing.py was run successfully.")

    except ValueError as e:
        logger.error('Bikes data unable to be added to "bike_stock" database. Try checking the dimensions of the data'
                     'and try again.')
        logger.error(e)
        sys.exit(1)
