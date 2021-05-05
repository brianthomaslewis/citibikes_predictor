#!/usr/bin/env python
# coding: utf-8

# In[7]:

import os
import glob
import csv
import itertools
import zipfile
import datetime
import shutil
import time
import requests
import pandas as pd
from src.bq_helper import BigQueryHelper
from multiprocessing.pool import ThreadPool


# In[8]:

def download_stations_data(json_path, stations_output_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path

    # STEP 1: Acquire snapshot of station-level bicycle capacity for later stock calculations
    nyc_bikes = BigQueryHelper(active_project="bigquery-public-data",
                               dataset_name="new_york_citibike")

    query1 = """
        SELECT
          station_id, name, latitude, longitude, capacity, num_bikes_available, last_reported
        FROM
          `bigquery-public-data.new_york_citibike.citibike_stations`
        ORDER BY
          last_reported DESC
             """
    response1 = nyc_bikes.query_to_pandas_safe(query1, max_gb_scanned=10)
    response1.to_csv(stations_output_path, index=False)

def download_trips_data(zip_data_path, csv_data_path, output_csv_path):
    # STEP 0: Toggle options and paths
    # Range of raw data months to download (full range as of 2021-05-04 is from 2013-06 to 2021-03)

    ## ADD THIS AS AN OPTION
    month_start = '201306'
    month_end = '202103'

    # Specify local filepath and URL stems + suffix for downloading
    ### ADD EXCEPTION HANDLING
    shutil.rmtree(zip_data_path)  # './data/raw_data'
    shutil.rmtree(csv_data_path)  # './data/csv_data'
    os.mkdir(zip_data_path)
    os.mkdir(csv_data_path)
    path_stem = zip_data_path
    url_stem = 'https://s3.amazonaws.com/tripdata/'
    suffix_16 = '-citibike-tripdata.zip'
    suffix_21 = '-citibike-tripdata.csv.zip'
    csv_stem = csv_data_path

    # Initialize empty lists
    urls = []
    pr_paths = []
    yrmo = []

    # In[9]:

    # STEP 1: Create iterables for batch downloading
    # Function to download raw zip files from URL and download them to local path
    def url_response(url):
        f_path, url = url
        r = requests.get(url, stream=True)
        with open(f_path, 'wb') as f:
            for ch in r:
                f.write(ch)

    # Functions to produce YYYYMM strings to iterate over URL and filepaths for batch downloading
    def to_month(yyyymm):
        yr, mo = int(yyyymm[:4]), int(yyyymm[4:])
        return yr * 12 + mo

    def iter_months(start, end):
        for month in range(to_month(start), to_month(end) + 1):
            yr, mo = divmod(month - 1, 12)  # ugly fix to compensate
            yield yr, mo + 1  # for 12 % 12 == 0

    # Create list 'yrmo' with all desired dates in YYYYMM format
    for y, m in iter_months(month_start, month_end):
        if m % 13 < 10:
            yrmo.append(f'{y}0{m}')
        else:
            yrmo.append(f'{y}{m}')

    # Create path and URL lists for batch downloading and processing
    for date in yrmo:
        if date in yrmo[0:43]:  # Filepaths change after 201612
            urls.append([
                f'{path_stem}{date}{suffix_16}',  # Path to which you want .zip downloaded
                f'{url_stem}{date}{suffix_16}'])  # URL path of associated file
            pr_paths.append([
                f'{path_stem}{date}{suffix_16}',  # Path from which you want to load .zip file
                f'{csv_stem}citibikes_{date}.csv'])  # Path to which you want to save processed .csv file
        else:
            urls.append([
                f'{path_stem}{date}{suffix_21}',  # Path to which you want .zip downloaded
                f'{url_stem}{date}{suffix_21}'])  # URL path of associated file
            pr_paths.append([
                f'{path_stem}{date}{suffix_21}',  # Path from which you want to load .zip file
                f'{csv_stem}citibikes_{date}.csv'])  # Path to which you want to save processed .csv file

    # In[10]:

    # STEP 2: Download raw files from URL locations to local paths

    # NOTE: Total raw zip folders total approximately 4.5 GB
    ThreadPool(9).imap_unordered(url_response, urls)
    time.sleep(240)

    # In[11]:

    # STEP 3: Open, aggregate, and save processed data. These total ~560 MB

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

    # STEP 4: Consolidate all .csv files into one file, totaling ~590 MB

    files = glob.glob(f'{csv_stem}*.csv')
    df = pd.concat((pd.read_csv(f, usecols=[1, 2, 3, 4, 5]) for f in files))

    df.to_csv(output_csv_path, index=False)  # './data/trips_output.csv'

    # STEP 5: Remove raw and intermediate data (if desired)

    shutil.rmtree(csv_stem)
    shutil.rmtree(path_stem)
