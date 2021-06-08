import sys
import logging
import logging.config
import yaml
import argparse
import pandas as pd
import numpy as np
import src.config as connection_config
from src.helper_db import add_to_database
from src.helper_s3 import download_csv_s3, upload_to_s3
from src.data_processing import run_data_processing
from src.model_run import run_train_models

# Logging
logging.config.fileConfig("config/logging/local.conf",
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logging.getLogger("run_modeling")

"""Script to take acquired data and run processing and modeling functions"""


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get citi bikes data from s3 and prep for modeling')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='path to yaml file with configurations')
    parser.add_argument("--engine_string", default=connection_config.SQLALCHEMY_DATABASE_URI,
                        help="Manually specified engine location.")
    parser.add_argument("--local", dest='local_flag', action='store_true',
                        help="Use arg if you want to load from local rather than S3.")
    parser.add_argument("--s3_bucket", default=connection_config.S3_BUCKET, help="s3 bucket name")
    args = parser.parse_args()
    run_data_processing(args)
    run_train_models(args)
    logger.info('run_modeling.py was run successfully.')
