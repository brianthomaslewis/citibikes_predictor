import os
from os import path
import yaml
DEBUG = True
PORT = 5000
APP_NAME = "citibikes-predictor"
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100

# Getting the parent directory of this file. That will function as the project home.
PROJECT_HOME = path.dirname(path.dirname(path.abspath(__file__)))

# Logging
LOGGING_CONFIG = path.join(PROJECT_HOME, 'config/logging/local.conf')

# File paths config
FILE_CONFIG = path.join(PROJECT_HOME, 'config/config.yaml')

# open yaml with file and s3 bucket paths
with open(FILE_CONFIG, 'r') as f:
    file_config = yaml.load(f, Loader=yaml.FullLoader)

# Google BigQuery / Citibike Stations data info #
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
BIGQUERY_PROJECT = 'bigquery-public-data'
BIGQUERY_DATASET = 'new_york_citibike'
BIGQUERY_QUERY = """
        SELECT
          station_id, name, latitude, longitude, capacity, num_bikes_available, last_reported
        FROM
          `bigquery-public-data.new_york_citibike.citibike_stations`
        ORDER BY
          last_reported DESC
                 """
STATIONS_FILE_LOCATION = file_config['local']['STATIONS_FILE_LOCATION']

# Citibike Trips data download specifications #
YRMO_START = '201306'  # data begin in 201306
YRMO_END = '202103'  # data end in 202103
TRIPS_ZIP_LOCATION = file_config['local']['TRIPS_ZIP_LOCATION']
TRIPS_CSV_LOCATION = file_config['local']['TRIPS_CSV_LOCATION']
TRIPS_FILE_LOCATION = file_config['local']['TRIPS_FILE_LOCATION']
TRIPS_URL_STEM = 'https://s3.amazonaws.com/tripdata/'
TRIPS_SUFFIX_1 = '-citibike-tripdata.zip'
TRIPS_SUFFIX_2 = '-citibike-tripdata.csv.zip'
TRIPS_LABEL_CHUNK = 'citibikes_'
TRIPS_THREADS = 8
TRIPS_SLEEP_TIME = 240  # Seconds to sleep while downloading with threads

# AWS S3 Bucket and Object Names Setup #
S3_BUCKETNAME = file_config['aws-s3']['S3_BUCKETNAME']
S3_DIRECTORY = file_config['aws-s3']['S3_DIRECTORY']
S3_STATIONS = file_config['aws-s3']['S3_STATIONS']
S3_TRIPS = file_config['aws-s3']['S3_TRIPS']

# Connection string
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('DATABASE_NAME')
DB_DIALECT = 'mysql+pymysql'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/msia423_db.db'
else:
    SQLALCHEMY_DATABASE_URI = '{dialect}://{user}:{pw}@{host}:{port}/{db}'.format(dialect=DB_DIALECT, user=DB_USER,
                                                                                 pw=DB_PW, host=DB_HOST, port=DB_PORT,
                                                                                 db=DATABASE)
