import os
import sys
import logging
import requests
import json
from urllib.request import urlopen
import pandas as pd
from src.helper_db import add_to_database
from src.helper_s3 import upload_to_s3

# Logging
logger = logging.getLogger(__name__)


def download_stations_data(url, stations_output_path, s3_bucket, s3_directory, engine_string):
    """
    Takes the .json file from NYC Citi Bike feed and obtains stations data based on it.

    Args:
        url (str): URL of NYC Citi Bike feed .json file containing station data
        stations_output_path (str): location to write file to.
        s3_bucket (str): Name of S3 bucket to write data
        s3_directory (str): String of S3 directory in which to house data
        engine_string (str): optional engine string to specify where MySQL database is located

    Returns: None (df written to specified location at stations_output_path)

    """

    # file path needs to be provided
    if not stations_output_path:
        logger.error('Please provide a valid `stations_output_path` and try again.')
        raise ValueError

    try:
        jsonurl = urlopen(url)
        text = json.loads(jsonurl.read())
        response = pd.json_normalize(text, record_path=['stationBeanList'])
        response['station_id'] = response['id']
        response['name'] = response['stationName']
        response['capacity'] = response['totalDocks']
        response['num_bikes_available'] = response['totalDocks'] - response['availableDocks']
        response['last_reported'] = pd.to_datetime(response['lastCommunicationTime']).dt.date

        response = response[['station_id', 'name', 'latitude', 'longitude', 'capacity',
                             'num_bikes_available', 'last_reported']]
        logger.info('Preview of the stations data: ')
        print(response.head())

    except ConnectionError as e:
        logger.error("There was a connection error to the NYC Citi Bike stations .json feed. "
                     "Please verify the URL and try again.")
        logger.error(e)
        sys.exit(1)

    # Add stations data to local output
    response.to_csv(stations_output_path, index=False)
    logger.info("Success! Wrote Citi Bike stations data to local filepath '%s'.", stations_output_path)

    # Add stations data to S3 bucket
    upload_to_s3(stations_output_path, s3_bucket, s3_directory)
    logger.info("Success! Wrote Citi Bike stations data to '%s' S3 bucket in '%s' folder.", s3_bucket, s3_directory)

    # Add pared-down stations data to MySQL database
    response_trimmed = response[['station_id', 'name', 'latitude', 'longitude']]
    add_to_database(response_trimmed, "stations", 'replace', engine_string)
    logger.info("Success! Wrote Citi Bike stations data to MySQL database.")


