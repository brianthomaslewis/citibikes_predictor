# Functions to produce YYYYMM strings to iterate over URL and filepaths for batch downloading
def to_month(yyyymm):
    """Helper function to iterate through months"""
    yr, mo = int(yyyymm[:4]), int(yyyymm[4:])
    return yr * 12 + mo

def iter_months(start, end):
    """Helper function to create YYYYMM objects"""
    for month in range(to_month(start), to_month(end) + 1):
        yr, mo = divmod(month - 1, 12)
        yield yr, mo + 1  # for 12 % 12 == 0