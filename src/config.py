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

# S3 Bucket name
S3_BUCKET = os.environ.get('S3_BUCKET')
if S3_BUCKET is not None:
    pass
elif S3_BUCKET is None:
    S3_BUCKET = file_config['data_acquisition']['s3_bucket']

# Connection string
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('MYSQL_DATABASE')
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
