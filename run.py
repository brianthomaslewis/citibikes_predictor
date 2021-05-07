import argparse
from src.download_data import acquire_data
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

    # Sub-parser for downloading raw data from Citibike and uploading to S3
    sb_download = subparsers.add_parser("download_raw_data", description="Download Citibike data and store in S3")
    sb_download.add_argument("--s3_bucket", default='2021-msia423-lewis-brian', help="s3 bucket name")
    sb_download.add_argument("--s3_directory", default='raw/', help="s3 bucket directory to write file to")
    # sb_download.set_defaults(func=acquire_data())

    # Sub-parser for creating a database
    sb_create_db = subparsers.add_parser("create_db", description="Creates a database in RDS/locally with raw data")
    # sb_create_db.set_defaults(func=create_db())

    # sb_download_raw_data = subparsers.add_parser("download_raw_data", description="Download data from internet")
    # sb_download_raw_data.add_argument("--json_path", default=BIGQUERY_CREDENTIALS_PATH,
    #                                   help="Google BigQuery credentials")
    # sb_download_raw_data.add_argument("--stations_output_path", default='data/stations_output.csv',
    #                                   help="Stations data output path")
    # sb_download_raw_data.add_argument("--zip_data_path", default='data/raw_data/',
    # help="path for .zip file downloads")
    # sb_download_raw_data.add_argument("--csv_data_path", default='data/csv_data/',
    # help="path for intermediate .csv file downloads")
    # sb_download_raw_data.add_argument("--output_csv_path", default='data/trips_output.csv',
    # help="path for trips data output")

    # # Sub-parser for uploading data to S3
    # sb_upload_to_s3 = subparsers.add_parser("upload_to_s3", description="Upload processed data to s3")
    # sb_upload_to_s3.add_argument("--local_path", default='data/stations_output.csv',
    #                              help="Where data is originating that is being uploaded to S3")
    # sb_upload_to_s3.add_argument("--s3path", default='s3://2021-msia423-lewis-brian/raw/stations_output.csv',
    #                              help="Where to load data in to s3")
    #
    # # Sub-parser for creating a database
    # sb_create = subparsers.add_parser("create_db", description="Create database")
    # sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
    #                        help="SQLAlchemy connection URI for database")


    args = parser.parse_args()
    # args.func(args)
    sp_used = args.subparser_name
    if sp_used == 'download_raw_data':
        acquire_data(args.s3_bucket, args.s3_directory)
    # elif sp_used == 'upload_to_s3':
    #     upload_to_s3(args.local_path, args.s3path)
    elif sp_used == 'create_db':
        create_db()
    # # elif sp_used == 'ingest':
    # #     tm = TrackManager(engine_string=args.engine_string)
    # #     tm.add_track(args.title, args.artist, args.album)
    # #     tm.close()
    # else:
    #     parser.print_help()
