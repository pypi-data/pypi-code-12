from __future__ import absolute_import
from datetime import timedelta


def start_of_day(date):
    """
    Return a new datetime with values that represent a start of a day.
    :param date: Date to ...
    :type date: datetime.datetime
    :rtype: datetime.datetime
    """
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(date):
    """
    Return a new datetime with values that represent a end of a day.
    :param date: Date to ...
    :type date: datetime.datetime
    :rtype: datetime.datetime
    """
    return start_of_day(date) + timedelta(days=1, microseconds=-1)


def start_of_month(date):
    """
    Return a new datetime with values that represent a start of a month.
    :param date: Date to ...
    :type date: datetime.datetime
    :rtype: datetime.datetime
    """
    return start_of_day(date).replace(day=1)


def end_of_month(date):
    """
    Return a new datetime with values that represent a end of a month.
    :param date: Date to ...
    :type date: datetime.datetime
    :rtype: datetime.datetime
    """
    if date.month == 12:
        return start_of_month(date).replace(year=date.year + 1, month=1) - timedelta(microseconds=1)
    else:
        return start_of_month(date).replace(month=date.month + 1) - timedelta(microseconds=1)
