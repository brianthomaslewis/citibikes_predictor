import argparse
import logging.config
from src.download_citibikes_data import download_trips_data, download_stations_data
from src.upload_to_s3 import upload_to_s3
from src.create_db import create_db
from config.flaskconfig import SQLALCHEMY_DATABASE_URI, BIGQUERY_CREDENTIALS_PATH

# Logger information
logging.config.fileConfig('config/logging/local.conf')
logger = logging.getLogger('penny-lane-pipeline')

if __name__ == '__main__':

    # Add parsers for both creating a database and adding songs to it
    parser = argparse.ArgumentParser(description="Add data to S3 bucket")
    subparsers = parser.add_subparsers(dest='subparser_name')

    # Sub-parser for downloading raw data from Citibike
    sb_download_raw_data = subparsers.add_parser("download_raw_data", description="Download data from internet")
    sb_download_raw_data.add_argument("--json_path", default=BIGQUERY_CREDENTIALS_PATH,
                                      help="Google BigQuery credentials")
    sb_download_raw_data.add_argument("--stations_output_path", default='data/stations_output.csv',
                                      help="Stations data output path")
    sb_download_raw_data.add_argument("--zip_data_path", default='data/raw_data/', help="path for .zip file downloads")
    sb_download_raw_data.add_argument("--csv_data_path", default='data/csv_data/', help="path for intermediate .csv file downloads")
    sb_download_raw_data.add_argument("--output_csv_path", default='data/trips_output.csv', help="path for trips data output")

    # Sub-parser for uploading data to S3
    sb_upload_to_s3 = subparsers.add_parser("upload_to_s3", description="Upload processed data to s3")
    sb_upload_to_s3.add_argument("--local_path", default='data/stations_output.csv',
                                 help="Where data is originating that is being uploaded to S3")
    sb_upload_to_s3.add_argument("--s3path", default='s3://2021-msia423-lewis-brian/raw/stations_output.csv',
                                 help="Where to load data in to s3")

    # Sub-parser for creating a database
    sb_create = subparsers.add_parser("create_db", description="Create database")
    sb_create.add_argument("--engine_string", default=SQLALCHEMY_DATABASE_URI,
                           help="SQLAlchemy connection URI for database")

    # Sub-parser for ingesting new data
    # sb_ingest = subparsers.add_parser("ingest", description="Add data to database")
    # sb_ingest.add_argument("--artist", default="Emancipator", help="Artist of song to be added")
    # sb_ingest.add_argument("--title", default="Minor Cause", help="Title of song to be added")
    # sb_ingest.add_argument("--album", default="Dusk to Dawn", help="Album of song being added")
    # sb_ingest.add_argument("--engine_string", default='sqlite:///data/tracks.db',
    #                        help="SQLAlchemy connection URI for database")

    args = parser.parse_args()
    sp_used = args.subparser_name
    if sp_used == 'download_raw_data':
        download_stations_data(args.json_path, args.stations_output_path)
        download_trips_data(args.zip_data_path, args.csv_data_path, args.output_csv_path)
    elif sp_used == 'upload_to_s3':
        upload_to_s3(args.local_path, args.s3path)
    elif sp_used == 'create_db':
        create_db(args.engine_string)
    # elif sp_used == 'ingest':
    #     tm = TrackManager(engine_string=args.engine_string)
    #     tm.add_track(args.title, args.artist, args.album)
    #     tm.close()
    else:
        parser.print_help()
