import boto3
import sys
import botocore.exceptions as botoexceptions
import logging.config
import logging
import os
import pandas as pd

# Logging
logger = logging.getLogger(__name__)


def upload_to_s3(file_local_path, s3_bucket, s3_directory):
    """
    Takes path of locally written df and writes it to S3 bucket.

    Args:
        file_local_path (str): Path of file that will be uploaded to S3
        s3_bucket (str): S3 bucket name without the 's3://' prefix needed
        s3_directory (str): Directory within S3 bucket within which to write the data.

    Returns: none (writes files to S3)

    """

    try:
        s3 = boto3.resource("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. Verify that they have been "
                     "made available as detailed in readme instructions")
        sys.exit(1)
    except Exception as e:
        logger.error(e)
        logger.error("Unable to connect to s3. Verify your AWS credentials and connection and try again.")
        sys.exit(1)

    logger.info("Writing files to S3.")

    s3_file_path = f'{s3_directory}{os.path.basename(os.path.normpath(file_local_path))}'

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_local_path, s3_bucket, s3_file_path)
    except ClientError as err:
        logging.error(err)


def download_csv_s3(s3_bucket_name, bucket_dir_path, input_filename, output_filename):
    """
    Obtains selected .csv file from s3 bucket, downloads it to output_filename, and returns a dataframe
    Args:
        s3_bucket_name (str): the name of S3 bucket containing data of interest
        bucket_dir_path (str): s3 bucket file path where data is located
        input_filename (str): filename containing data of interest
        output_filename (str): filename of where to download data from s3
    Returns:
        data_df (pandas DataFrame): DataFrame pulled from selected S3 bucket
    """

    # Connect to s3 prior to starting up any processing
    try:
        s3 = boto3.client("s3")
    except botoexceptions.NoCredentialsError:
        logger.error("Your AWS credentials were not found. "
                     "Verify that they have been passed to the environment as instructed in README.")
        sys.exit(1)

    # If filename specified, pull the requisite data
    if input_filename is not None:
        try:
            s3_file = os.path.join(bucket_dir_path, input_filename)
            logger.debug("user inputted file path:%s", s3_file)
            # s3_obj = s3.get_object(s3_bucket_name, s3_file)
            s3.download_file(s3_bucket_name, s3_file, output_filename)
        except botoexceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                logger.error("The object does not exist. Verify path and filename.")
            else:
                logger.error("Unexpected error trying to retrieve s3 object. %s", e.response['Error'])
            sys.exit(1)

    # If filename not specified, require the user to input filename
    else:
        logger.error("No specified filepath. Please re-enter filename and try again.")
        sys.exit(1)

    # Raw data should be in CSV form, throw exception if not in CSV form
    try:
        data_df = pd.read_csv(output_filename)
        logger.info("Successfully retrieved data from s3")
    except TypeError:
        logger.error("")
    except ValueError:
        logger.error("Selected file in s3 directory is not in CSV form. Please respecify the file and try again")
        sys.exit(1)
    except Exception as error:
        logger.error("Unexpected error in parsing s3 data: %s:%s", type(error).__name__, error)
        sys.exit(1)

    return data_df
