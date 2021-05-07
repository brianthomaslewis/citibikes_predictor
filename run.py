import argparse
from src.acquire_data import acquire_data
from src.create_db import create_db
import src.config as config

import logging.config

# Logger information
logging.config.fileConfig(config.LOGGING_CONFIG, disable_existing_loggers=False)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # Add parsers for both creating a database and adding data to it
    parser = argparse.ArgumentParser(description="Run components of the source code")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for downloading raw data from Citi Bike and uploading to S3
    sb_download = subparsers.add_parser("download_raw_data", description="Download Citibike data and store in S3")
    sb_download.add_argument("--trips_only", default='FALSE', help="Toggle for downloading only 'trips' dataset")
    sb_download.add_argument("--s3_bucket", default='2021-msia423-lewis-brian', help="s3 bucket name")
    sb_download.add_argument("--s3_directory", default='raw/', help="s3 bucket directory to write file to")

    # Sub-parser for creating a database
    sb_create_db = subparsers.add_parser("create_db", description="Creates a database in RDS/locally with raw data")
    sb_create_db.add_argument("--engine_string", default=config.SQLALCHEMY_DATABASE_URI,
                              help="Manually specified engine location.")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'download_raw_data':
        acquire_data(args.trips_only, args.s3_bucket, args.s3_directory)
    elif sp_used == 'create_db':
        create_db(args.engine_string)