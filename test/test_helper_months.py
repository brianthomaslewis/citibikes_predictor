from datetime import datetime
import pytest
import pandas as pd
import src.helper_months as hm


def test_to_month():
    string = '201904'

    expected_output = 24232

    output = hm.to_month(string)

    assert expected_output == output


def test_to_month_unhappy():
    string = '201904'

    expected_output = None

    output = hm.to_month(string)

    assert not expected_output == output


def test_iter_months():
    start = '201902'
    end = '202003'

    expected_output = [(2019, 2), (2019, 3), (2019, 4), (2019, 5), (2019, 6), (2019, 7), (2019, 8), (2019, 9),
                       (2019, 10), (2019, 11), (2019, 12), (2020, 1), (2020, 2), (2020, 3)]

    output = list(hm.iter_months(start, end))

    assert expected_output == output


def test_iter_months_unhappy():
    start = '201902'
    end = '202003'

    expected_output = [(2012, 2), (2019, 3), (2019, 4), (2019, 5), (2019, 6), (2019, 7), (2019, 8), (2019, 9),
                       (2019, 10), (2019, 11), (2019, 12), (2020, 1), (2020, 2), (2020, 3)]

    output = list(hm.iter_months(start, end))

    assert expected_output != output


def test_date_range_hours():
    start_date = datetime(year=2021, month=4, day=1, hour=0, minute=00)
    end_date = datetime(year=2021, month=4, day=2, hour=0, minute=00)

    expected_output = ['2021-04-01 00:00', '2021-04-01 01:00', '2021-04-01 02:00', '2021-04-01 03:00',
                       '2021-04-01 04:00', '2021-04-01 05:00', '2021-04-01 06:00', '2021-04-01 07:00',
                       '2021-04-01 08:00', '2021-04-01 09:00', '2021-04-01 10:00', '2021-04-01 11:00',
                       '2021-04-01 12:00', '2021-04-01 13:00', '2021-04-01 14:00', '2021-04-01 15:00',
                       '2021-04-01 16:00', '2021-04-01 17:00', '2021-04-01 18:00', '2021-04-01 19:00',
                       '2021-04-01 20:00', '2021-04-01 21:00', '2021-04-01 22:00', '2021-04-01 23:00']

    output = []

    for single_date in hm.date_range_hours(start_date, end_date):
        output.append(single_date.strftime("%Y-%m-%d %H:%M"))

    assert expected_output == output


def test_date_range_hours_unhappy():
    start_date = datetime(year=2017, month=12, day=18, hour=9, minute=4)
    end_date = datetime(year=2021, month=4, day=2, hour=0, minute=00)

    expected_output = ['2021-04-01 00:00', '2021-04-01 01:00', '2021-04-01 02:00', '2021-04-01 03:00',
                       '2021-04-01 04:00', '2021-04-01 05:00', '2021-04-01 06:00', '2021-04-01 07:00',
                       '2021-04-01 08:00', '2021-04-01 09:00', '2021-04-01 10:00', '2021-04-01 11:00',
                       '2021-04-01 12:00', '2021-04-01 13:00', '2021-04-01 14:00', '2021-04-01 15:00',
                       '2021-04-01 16:00', '2021-04-01 17:00', '2021-04-01 18:00', '2021-04-01 19:00',
                       '2021-04-01 20:00', '2021-04-01 21:00', '2021-04-01 22:00', '2021-04-01 23:00']

    output = []

    for single_date in hm.date_range_hours(start_date, end_date):
        output.append(single_date.strftime("%Y-%m-%d %H:%M"))

    assert expected_output != output
