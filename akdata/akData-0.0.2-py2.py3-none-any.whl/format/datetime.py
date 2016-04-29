from __future__ import absolute_import

from datetime import date,datetime


def formatDatetime(d,skipTimeIfZero=False,alwaysSkipTime=False,datetimeFormat='%d/%m/%Y %H:%M:%S',dateFormat='%d/%m/%Y',noneValue='-',):
    """Formats date/time but only includes time if it's not 0:00:00. Also formats a date. Formats a None value separately."""
    # if don't always skip time and is datetime and (don't skip time of zero or time is not zero)
    if not alwaysSkipTime and isinstance(d,datetime.datetime) and (not skipTimeIfZero or d.second>0 or d.minute>0 or d.hour>0):
        return d.strftime(datetimeFormat)
    elif isinstance(d,date):
        # datetime is also a date, so datetimes that have a zero time still get here
        return d.strftime(dateFormat)
    return noneValue


def formatDate(d,dateFormat='%d/%m/%Y',noneValue='-'):
    """Formats a date only."""
    return formatDatetime(d,alwaysSkipTime=True,dateFormat=dateFormat,noneValue=noneValue)
