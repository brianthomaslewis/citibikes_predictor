"""Tests for data_processing.py module."""
import pytest
import pandas as pd
from src.data_processing import process_bike_data

raw_trips_columns = ['station_id', 'date', 'hour', 'inflows', 'outflows']

raw_trips = [[72, '2020-03-01', 6, 1, 3],
             [72, '2020-03-01', 9, 6, 3],
             [72, '2020-03-01', 10, 2, 4],
             [72, '2020-03-01', 11, 2, 2],
             [72, '2020-03-01', 12, 3, 5],
             [72, '2020-03-01', 13, 2, 3],
             [72, '2020-03-01', 14, 4, 4],
             [72, '2020-03-01', 15, 4, 4]]

raw_stations_columns = ['station_id', 'name', 'latitude', 'longitude',
                        'capacity', 'num_bikes_available', 'last_reported']

raw_stations = [
    [72, 'W 52 St & 11 Ave', 40.76727216, -73.99392888, 39, 7, '2016-01-22'],
    [79, 'Franklin St & W Broadway', 40.71911552, -74.00666661, 33, 33, '2016-01-22'],
    [82, 'St James Pl & Pearl St', 40.71117416, -74.00016545, 27, 0, '2016-01-22'],
    [83, 'Atlantic Ave & Fort Greene Pl', 40.68382604, -73.97632328, 62, 41, '2016-01-22'],
    [116, 'W 17 St & 8 Ave', 40.74177603, -74.00149746, 39, 20, '2016-01-22'],
    [119, 'Park Ave & St Edwards St', 40.69608941, -73.97803415, 19, 4, '2016-01-22'],
    [120, 'Lexington Ave & Classon Ave', 40.68676793, -73.95928168, 19, 2, '2016-01-22'],
    [127, 'Barrow St & Hudson St', 40.73172428, -74.00674436, 31, 10, '2016-01-22']
]


def test_process_bike_data():
    """Test for process_bike_data happy path"""
    trips = pd.DataFrame(raw_trips, columns=raw_trips_columns)

    stations = pd.DataFrame(raw_stations, columns=raw_stations_columns)

    expected_output = pd.DataFrame({
        'station_id': [72, 72, 72, 72, 72, 72, 72, 72],
        'date': ['2020-03-01 06:00:00', '2020-03-01 09:00:00',
                 '2020-03-01 10:00:00', '2020-03-01 11:00:00',
                 '2020-03-01 12:00:00', '2020-03-01 13:00:00',
                 '2020-03-01 14:00:00', '2020-03-01 15:00:00'],
        'name': ['W 52 St & 11 Ave', 'W 52 St & 11 Ave',
                 'W 52 St & 11 Ave', 'W 52 St & 11 Ave',
                 'W 52 St & 11 Ave', 'W 52 St & 11 Ave',
                 'W 52 St & 11 Ave', 'W 52 St & 11 Ave'],
        'latitude': [40.76727216, 40.76727216, 40.76727216, 40.76727216,
                     40.76727216, 40.76727216, 40.76727216, 40.76727216],
        'longitude': [-73.99392888, -73.99392888, -73.99392888, -73.99392888,
                      -73.99392888, -73.99392888, -73.99392888, -73.99392888],
        'stock': [25.0, 27.0, 24.0, 26.0, 26.0, 28.0, 29.0, 29.0]})

    convert_dict = {'station_id': int,
                    'date': 'datetime64',
                    'name': object,
                    'latitude': float,
                    'longitude': float,
                    'stock': float}

    expected_output = expected_output.astype(convert_dict)

    output = process_bike_data(trips, stations, 0.65)

    assert expected_output.equals(output)


def test_process_bike_data_unhappy():
    """Test for process_bike_data unhappy path"""
    trips = pd.DataFrame(raw_trips, columns=raw_trips_columns)

    stations = pd.DataFrame(raw_stations, columns=raw_stations_columns)

    expected_output = None

    output = process_bike_data(trips, stations, 0.65)

    assert not output.equals(expected_output)
