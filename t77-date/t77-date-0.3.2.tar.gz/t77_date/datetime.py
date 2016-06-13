from __future__ import absolute_import
from datetime import timedelta, date, datetime


def start_of_day(val):
    """
    Return a new datetime with values that represent a start of a day.
    :param val: Date to ...
    :type val: datetime.datetime | datetime.date
    :rtype: datetime.datetime
    """
    if type(val) == date:
        val = datetime.fromordinal(val.toordinal())
    return val.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(val):
    """
    Return a new datetime with values that represent a end of a day.
    :param val: Date to ...
    :type val: datetime.datetime | datetime.date
    :rtype: datetime.datetime
    """
    if type(val) == date:
        val = datetime.fromordinal(val.toordinal())
    return start_of_day(val) + timedelta(days=1, microseconds=-1)


def start_of_month(val):
    """
    Return a new datetime with values that represent a start of a month.
    :param val: Date to ...
    :type val: datetime.datetime | datetime.date
    :rtype: datetime.datetime
    """
    if type(val) == date:
        val = datetime.fromordinal(val.toordinal())
    return start_of_day(val).replace(day=1)


def end_of_month(val):
    """
    Return a new datetime with values that represent a end of a month.
    :param val: Date to ...
    :type val: datetime.datetime | datetime.date
    :rtype: datetime.datetime
    """
    if type(val) == date:
        val = datetime.fromordinal(val.toordinal())
    if val.month == 12:
        return start_of_month(val).replace(year=val.year + 1, month=1) - timedelta(microseconds=1)
    else:
        return start_of_month(val).replace(month=val.month + 1) - timedelta(microseconds=1)
