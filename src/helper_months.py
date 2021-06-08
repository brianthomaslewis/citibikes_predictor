from datetime import timedelta


def to_month(yyyymm):
    """
    Helper function to create dates in format fitting with `iter_months` function
    Args:
        yyyymm (str): A date string representing year and month in the YYYYMM format
    Returns:
        (str): A combined str representing the year-month combination for iterating in the following function
    """
    yr, mo = int(yyyymm[:4]), int(yyyymm[4:])
    return yr * 12 + mo


def iter_months(start, end):
    """
    Helper function to create YYYYMM objects
    Args:
        start (str): A date string representing the starting year and month in YYYYMM format of the iteration block
        end (str): A date string representing the ending year and month in YYYYMM format of the iteration block
    Returns:
        yr (int): A calculated int representing the year for iterating
        mo (int): A calculated int representing the month for iterating
    """
    for month in range(to_month(start), to_month(end) + 1):
        yr, mo = divmod(month - 1, 12)
        yield yr, mo + 1  # for 12 % 12 == 0


def date_range(start_date, end_date):
    """
    Helper function to create hourly timestamp increments between two dates
    Args:
        start_date (date): A date object representing the starting date for calculating hourly timestamps
        end_date (date): A date object representing the ending date for calculating hourly timestamps
    Returns:
        (timestamp): A calculated int representing the year for iterating
    """
    delta = timedelta(hours=1)
    while start_date < end_date:
        yield start_date
        start_date += delta
