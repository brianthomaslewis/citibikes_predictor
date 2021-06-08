from datetime import datetime
import pytest
import pandas as pd
from src.model_run import model_fun


def test_model_fun():
    df = pd.read_csv('data/sample/sample_bike_stock.csv')
    start_date_args = {'year': 2021, 'month': 4, 'day': 1, 'hour': 0, 'minute': 00}
    end_date_args = {'year': 2021, 'month': 4, 'day': 1, 'hour': 8, 'minute': 00}
    model_params = {'p': 1, 'd': 0, 'q': 0}
    optional_fit_args = {'trend': 'c', 'method': 'css-mle', 'solver': 'lbfgs'}

    expected_output = pd.DataFrame({
        'station_id': [72, 72, 72, 72, 72, 72, 72, 72],
        'date': ['2021-04-01', '2021-04-01', '2021-04-01', '2021-04-01',
                 '2021-04-01', '2021-04-01', '2021-04-01', '2021-04-01'],
        'hour': [0, 1, 2, 3, 4, 5, 6, 7],
        'pred_num_bikes': [30, 29, 29, 29, 28, 28, 28, 28]})

    convert_dict = {'station_id': int,
                    'date': 'datetime64',
                    'hour': int,
                    'pred_num_bikes': int}

    expected_output = expected_output.astype(convert_dict)

    expected_output.date = expected_output.date.dt.date

    expected_mape = pd.DataFrame({'Station': [72], 'MAPE': [28.99973384558673]})

    output, mape = model_fun(df, start_date_args, end_date_args, model_params, optional_fit_args)

    assert expected_output.equals(output), expected_mape.equals(mape)


def test_model_fun_unhappy():
    df = pd.read_csv('data/sample/sample_bike_stock.csv')
    start_date_args = {'year': 2021, 'month': 4, 'day': 1, 'hour': 0, 'minute': 00}
    end_date_args = {'year': 2021, 'month': 4, 'day': 1, 'hour': 8, 'minute': 00}
    model_params = {'p': 1, 'd': 0, 'q': 0}
    optional_fit_args = {'trend': 'c', 'method': 'css-mle', 'solver': 'lbfgs'}

    expected_output = pd.DataFrame({
        'station_id': [72, 72, 72, 72, 72, 72, 72, 72],
        'date': ['2021-04-01', '2021-04-01', '2021-04-01', '2021-04-01',
                 '2021-04-01', '2021-04-01', '2021-04-01', '2021-04-01'],
        'hour': [0, 1, 2, 3, 4, 5, 6, 7],
        'pred_num_bikes': [66, -14, 22, 78, 100, 6000, -5, 0]})

    convert_dict = {'station_id': int,
                    'date': 'datetime64',
                    'hour': int,
                    'pred_num_bikes': int}

    expected_output = expected_output.astype(convert_dict)

    expected_output.date = expected_output.date.dt.date

    expected_mape = pd.DataFrame({'Station': [72], 'MAPE': [28.99973384558673]})

    output, mape = model_fun(df, start_date_args, end_date_args, model_params, optional_fit_args)

    assert not expected_output.equals(output), expected_mape.equals(mape)
