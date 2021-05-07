import sys
from src.download_stations_data import download_stations_data
from src.download_trips_data import download_trips_data
import logging
import boto3
import botocore.exceptions as botoexceptions
from botocore.exceptions import ClientError

import src.config as config
import logging.config

logging.config.fileConfig(fname=config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

"""
Download Citibike stations data, trips data and writes all downloaded raw data to s3 as well
"""


def acquire_data(s3_bucket, s3_directory):
    """
    runs all downloading scripts to generate all raw data and then writes them to s3 bucket by calling
    'writeRawToS3()' function

    Args:
        s3_bucket: S3 bucket name without the 's3://' prefix needed
        s3_directory: S3 bucket directory within which to write the file

    Returns: None--all data sets saved to paths specified in config.py

    """
    download_stations_data()
    download_trips_data()
    writeRawToS3(s3_bucket, s3_directory)


def upload_file(file_name, bucket, directory, file_suffix):
    """
    Uploads file to S3 bucket as specified in arguments.

    Args:
        file_name: File to upload
        bucket: S3 Bucket to upload to
        directory: Directory within S3 Bucket to load data to
        file_suffix: Last section of S3 url for data about to be written.

    Returns: None (performs uploading task to S3).

    """
    object_name = f'{directory}{file_suffix}'

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)


def writeRawToS3(s3_bucket=config.S3_BUCKETNAME, s3_directory=config.S3_DIRECTORY):
    """
    writes all the files from acquire_data() to S3 bucket specified in config.py

    Args:
        s3_bucket: S3 bucket name without the 's3://' prefix needed
        s3_directory: Directory within S3 bucket within which to write the data.

    Returns: none (writes files to S3)

    """

    try:
        s3 = boto3.resource("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Verify that they have been "
                     "made available as detailed in readme instructions")
        sys.exit(1)

    logger.info("Writing files to S3.")

    upload_file(config.STATIONS_FILE_LOCATION, s3_bucket, s3_directory, config.S3_STATIONS)
    upload_file(config.TRIPS_FILE_LOCATION, s3_bucket, s3_directory, config.S3_TRIPS)

if __name__ == '__main__':
    acquire_data()