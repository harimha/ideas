from pandas import Timestamp
from datetime import date, datetime, timedelta, time


def is_datetime_like(obj):
    '''
    date, datetime, timedelta, time, Timestamp 를 포함함
    '''
    if type(obj) in [date, datetime, timedelta, time, Timestamp]:
        return True
    else:
        return False

def is_timestamp(obj):
    return isinstance(obj, Timestamp)

