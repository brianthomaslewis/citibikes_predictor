import requests
import os
import logging.config
import pandas as pd
from src.bq_helper import BigQueryHelper
import src.config as config

logging.config.fileConfig(fname=config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def download_stations_data(stations_output_path=config.STATIONS_FILE_LOCATION, bq_project_name=config.BIGQUERY_PROJECT,
                           bq_dataset=config.BIGQUERY_DATASET, query=config.BIGQUERY_QUERY):
    """
    Takes the .json file with Google BigQuery credentials and queries Citibikes station-level data from Google's
    Citibikes BigQuery dataset.

    Args:
        stations_output_path: location to write file to.
        bq_project_name: the Google BigQuery project name.
        bq_dataset: the Google BigQuery dataset name.
        query: the SQL query to pass to Google BigQuery.

    Returns: None (df written to specified location at stations_output_path)

    """

    # file path needs to be provided
    if not stations_output_path:
        raise ValueError

    nyc_bikes = BigQueryHelper(active_project=bq_project_name,
                               dataset_name=bq_dataset)

    query1 = query

    try:
        logger.info("Attempting to query Google BigQuery for Citi Bike stations data.")
        response1 = nyc_bikes.query_to_pandas_safe(query1, max_gb_scanned=25)
    except requests.exceptions.ConnectionError:
        logger.error("There was a connection error to Google BigQuery. Please try again or verify the query.")
        sys.exit(1)

    response1.to_csv(stations_output_path, index=False)
    logger.info("Success! Wrote Citi Bike stations data to {}.".format(stations_output_path))
