import os
import glob
import csv
import itertools
import zipfile
import datetime
import shutil
import logging.config
from time import sleep
import requests
import pandas as pd
from pathlib import Path
from multiprocessing.pool import ThreadPool
from src.bq_helper import BigQueryHelper
from src.month_functions import to_month, iter_months
import src.config as config

logging.config.fileConfig(fname=config.LOGGING_CONFIG)
logger = logging.getLogger(__name__)

""" Script downloads Citibikes trips data for the YYYYMM periods specified in config.py
"""


def download_trips_data(month_start=config.YRMO_START, month_end=config.YRMO_END,
                        zip_data_path=config.TRIPS_ZIP_LOCATION, csv_data_path=config.TRIPS_CSV_LOCATION,
                        url_stem=config.TRIPS_URL_STEM, suffix_1=config.TRIPS_SUFFIX_1,
                        suffix_2=config.TRIPS_SUFFIX_2, label_chunk=config.TRIPS_LABEL_CHUNK,
                        threads=config.TRIPS_THREADS, sleep_time=config.TRIPS_SLEEP_TIME,
                        output_path=config.TRIPS_FILE_LOCATION):
    """
    Takes the YYYYMM and downloads all relevant Citibike trips data for that period from
    https://s3.amazonaws.com/tripdata/

    Args:
        month_start: the earliest YYYYMM from which to download the data
        month_end: the latest YYYYMM to which to download the data
        zip_data_path: folder location in which to keep/extract all intermediate .zip files
        csv_data_path: folder location in which to keep/extract all intermediate .csv files
        url_stem: URL stem for S3 bucket holding Citibikes raw data
        suffix_1: URL suffix 1 for S3 bucket holding Citibikes raw data
        suffix_2: URL suffix 2 for S3 bucket holding Citibikes raw data
        label_chunk: file path chunk for labeling intermediate datasets
        threads: Number of download threads to use for downloading
        sleep_time: Number of seconds to sleep while threaded pool downloading occurs
        output_path: file location to which the final output .csv will be written

    Returns: none (writes selected trips data to output_path)


    """

    # Specify local filepath and URL stems + suffix for downloading
    zip_path = Path(zip_data_path)
    if zip_path.exists() and zip_path.is_dir():
        shutil.rmtree(zip_path)
        logger.info("Creating temporary folder for raw .zip data for processing in {}.".format(zip_data_path))
    os.mkdir(zip_data_path)

    csv_path = Path(csv_data_path)
    if csv_path.exists() and csv_path.is_dir():
        shutil.rmtree(csv_path)
        logger.info("Creating temporary folder for intermediate .csv data for processing in {}.".format(csv_data_path))
    os.mkdir(csv_data_path)

    # Initialize empty lists
    urls = []
    pr_paths = []
    yrmo = []
    # trips_df = []

    # Create iterables for batch downloading

    # Function to download raw zip files from URL and download them to local path
    def url_response(url):
        """
        Takes the a url and downloads the file associated with it using the `requests` module.

        Args:
            url: the URL from which to download data.

        Returns: the file located at the above URL

        """
        f_path, url = url
        r = requests.get(url, stream=True)
        with open(f_path, 'wb') as f:
            for ch in r:
                f.write(ch)

    # Create list 'yrmo' with all desired dates in YYYYMM format
    for y, m in iter_months(month_start, month_end):
        if m % 13 < 10:
            yrmo.append(f'{y}0{m}')
        else:
            yrmo.append(f'{y}{m}')

    # Create path and URL lists for batch downloading and processing
    for date in yrmo:
        if date <= '201612':  # Filepath patterns change after 201612
            urls.append([
                f'{zip_data_path}{date}{suffix_1}',  # Path to which you want .zip downloaded
                f'{url_stem}{date}{suffix_1}'])  # URL path of associated file
            pr_paths.append([
                f'{zip_data_path}{date}{suffix_1}',  # Path from which you want to load .zip file
                f'{csv_data_path}{label_chunk}{date}.csv'])  # Path to which you want to save processed .csv file
        else:
            urls.append([
                f'{zip_data_path}{date}{suffix_2}',  # Path to which you want .zip downloaded
                f'{url_stem}{date}{suffix_2}'])  # URL path of associated file
            pr_paths.append([
                f'{zip_data_path}{date}{suffix_2}',  # Path from which you want to load .zip file
                f'{csv_data_path}{label_chunk}{date}.csv'])  # Path to which you want to save processed .csv file

    # Download raw zip files in ThreadPool
    try:
        ThreadPool(threads).imap_unordered(url_response, urls)
        logger.info("Downloading raw Citi Bike files from months {} to {} using {} threads to {}. "
                    "Sleep time during multi-thread download: {} seconds.".format(month_start, month_end, threads,
                                                                                  zip_data_path, sleep_time))
        sleep(sleep_time)  # Sleeping to give device sufficient time to download files.
    except requests.exceptions.ConnectionError as e:
        logger.error(e)
        logger.error("Could not connect. Try checking your internet connection and trying again.")
        sys.exit(1)

    # Open, process, aggregate, and save processed data.
    logger.info("Attempting to process downloaded .zip files into intermediate .csv files and saving to {}.".format(csv_data_path))
    try:
        for path in pr_paths:
            # Read in CSV and rename columns for ease of use
            zf = zipfile.ZipFile(path[0])  # Obtain zipper object of zip folder
            target = zf.namelist()[0]  # Extracts relevant .csv file from zip folder
            df = pd.read_csv(zf.open(target), usecols=[1, 2, 3, 7])
            df.columns = ['start_time', 'stop_time', 'start_station_id', 'end_station_id']

            # Create inflows table
            infl = df[['end_station_id', 'stop_time']].copy()
            infl.loc[:, 'stop_time'] = pd.to_datetime(infl['stop_time'], infer_datetime_format=True)
            infl.loc[:, 'date'] = infl['stop_time'].dt.date
            infl.loc[:, 'hour'] = infl['stop_time'].dt.hour
            infl.loc[:, 'inflows'] = 1
            infl.rename(columns={'end_station_id': 'station_id'}, inplace=True)
            infl.drop('stop_time', axis='columns', inplace=True)
            inflows = infl.groupby(['station_id', 'date', 'hour']).sum().reset_index()

            # Create outflows table
            outf = df[['start_station_id', 'start_time']].copy()
            outf.loc[:, 'start_time'] = pd.to_datetime(outf['start_time'], infer_datetime_format=True)
            outf.loc[:, 'date'] = outf['start_time'].dt.date
            outf.loc[:, 'hour'] = outf['start_time'].dt.hour
            outf.loc[:, 'outflows'] = 1
            outf.rename(columns={'start_station_id': 'station_id'}, inplace=True)
            outf.drop('start_time', axis='columns', inplace=True)
            outflows = outf.groupby(['station_id', 'date', 'hour']).sum().reset_index()

            # Create total table
            flows = pd.merge(inflows, outflows, on=['station_id', 'date', 'hour'])

            # Export to csv
            flows.to_csv(path[1])
            # trips_df.append(flows)

    except Exception as err:
        logger.error(err)
        logger.error("Multi-thread downloading did not complete as designed. Try specifying a higher '--thread' count "
                     "and higher '--sleep_time' value and try again.")
        sys.exit(1)

    # Consolidate all intermediate .csv files into one output file
    logger.info("Consolidating intermediate .csv files into trips .csv output.")
    files = glob.glob(f'{csv_data_path}*.csv')
    trips_df = pd.concat((pd.read_csv(f, usecols=[1, 2, 3, 4, 5]) for f in files))

    trips_df.to_csv(output_path, index=False)
    logger.info("Success! Wrote Citi Bikes trip output to {}.".format(output_path))

    # Remove raw and intermediate data (if output performed correctly)
    file = Path(output_path)
    if file.exists():
        shutil.rmtree(csv_data_path)
        shutil.rmtree(zip_data_path)
    else:
        logger.error("Download process to obtain output 'trips.csv' file not completed successfully. "
                     "Please try again or consider respecifying function options.")
        sys.exit(1)
