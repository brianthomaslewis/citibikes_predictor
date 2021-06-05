import sys
import logging
import logging.config
import argparse
import yaml
from botocore.exceptions import ClientError
from data_download_stations import download_stations_data
from data_download_trips import download_trips_data
import config as connection_config

logger = logging.getLogger(__name__)

"""
Download Citi Bike stations data, trips data and writes all from_s3 raw data to s3 as well
"""


def acquire_data(arguments):
    """
    Wrapper function that retrieves data from NYC Bike Feed API and Citi Bikes S3 bucket and then writes
    them to s3 bucket as specified in arguments

    Args:
        arguments: From argparse, should contain arguments.config and optionally, the following arguments:
            config (obj) : A config object
            s3_bucket (str): S3 bucket name passed in as a string
            engine_string (str): SQLAlchemy engine string
            threads (int): Number of threads for multithreaded download of trips data
            sleep_time (int): Number of seconds to sleep while multithread download occurs

    Returns: None--all data sets saved to paths specified in arguments and config object

    """
    # Pull in config file
    config = arguments.config

    # Run download_stations_data
    download_stations_data(url=config['download_stations_data']['url'],
                           stations_output_path=config['download_stations_data']['stations_output_path'],
                           s3_bucket=arguments.s3_bucket,
                           s3_directory=config['download_stations_data']['s3_directory'],
                           engine_string=arguments.engine_string)
    logger.info("Success! Downloaded stations data locally to '%s' and on s3 to '%s'",
                config['download_stations_data']['stations_output_path'], config['download_stations_data']['s3_bucket'])

    # Run download_trips_data
    download_trips_data(month_start=config['download_trips_data']['month_start'],
                        month_end=config['download_trips_data']['month_end'],
                        zip_data_path=config['download_trips_data']['zip_data_path'],
                        csv_data_path=config['download_trips_data']['csv_data_path'],
                        url_stem=config['download_trips_data']['url_stem'],
                        suffix_1=config['download_trips_data']['suffix_1'],
                        suffix_2=config['download_trips_data']['suffix_2'],
                        label_chunk=config['download_trips_data']['label_chunk'],
                        threads=arguments.threads,
                        sleep_time=arguments.sleep_time,
                        output_path=config['download_trips_data']['output_path'],
                        s3_bucket=arguments.s3_bucket,
                        s3_directory=config['download_trips_data']['s3_directory'])
    logger.info("Success! Downloaded trips data locally to '%s' and on s3 to '%s'",
                config['download_trips_data']['output_path'], config['download_trips_data']['s3_bucket'])


if __name__ == '__main__':
    try:
        with open('config/config.yaml', "r") as f:
            config_obj = yaml.load(f, Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")
        sys.exit(1)
    parser = argparse.ArgumentParser(description='Acquire stations and trips data from the web')
    parser.add_argument('--config', '-c', default=config_obj, help='path to yaml file with configurations')
    parser.add_argument("--threads", default=config_obj['download_trips_data']['threads'], help="s3 bucket name")
    parser.add_argument("--sleep_time", default=config_obj['download_trips_data']['sleep_time'], help="s3 bucket name")
    parser.add_argument("--s3_bucket", default=connection_config.S3_BUCKET, help="s3 bucket name")
    parser.add_argument("--engine_string", default=connection_config.SQLALCHEMY_DATABASE_URI,
                        help="Manually specified engine location.")

    args = parser.parse_args()
    acquire_data(args)
    logger.info("data_acquisition.py was run successfully.")
