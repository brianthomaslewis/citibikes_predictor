import pytest
import pandas as pd


def test_download_trips_data():
    """
    test for appropriate column headers from trips data download since some data manipulation is involved
    """

    # happy path
    input_df = pd.DataFrame(pd.read_csv('../data/trips.csv').columns.values.tolist())
    # read in fake data
    df_true  = pd.DataFrame(['station_id', 'date', 'hour', 'inflows', 'outflows'])
    assert input_df.equals(df_true)