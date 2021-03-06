"""Run full acquisition script to create database, download data, and acquire it into S3"""
import sys
import logging
import logging.config
import argparse
import yaml
from src.create_db import create_db
from src.data_acquisition import acquire_data
import src.config as connection_config

# Logging
logging.config.fileConfig("config/logging/local.conf",
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)
logging.getLogger("run_acquisition")


if __name__ == '__main__':
    try:
        with open('config/config.yaml', "r") as f:
            config_obj = yaml.load(f, Loader=yaml.FullLoader)
    except IOError:
        logger.error("Could not read in the config file--verify correct filename/path.")
        sys.exit(1)
    parser = argparse.ArgumentParser(description='Acquire stations and trips data from the web')
    parser.add_argument('--config', '-c', default=config_obj,
                        help='path to yaml file with configurations')
    parser.add_argument("--threads", default=config_obj['download_trips_data']['threads'],
                        help="s3 bucket name")
    parser.add_argument("--sleep_time", default=config_obj['download_trips_data']['sleep_time'],
                        help="s3 bucket name")
    parser.add_argument("--s3_bucket", default=connection_config.S3_BUCKET,
                        help="s3 bucket name")
    parser.add_argument("--engine_string", default=connection_config.SQLALCHEMY_DATABASE_URI,
                        help="Manually specified engine location.")

    args = parser.parse_args()
    create_db(args)
    acquire_data(args)
    logger.info("run_acquisition.py was run successfully.")
