# -*- encoding: utf-8 -*-
import calendar
import pytz
from datetime import timedelta
from six import iteritems

def add_month(date, number):
    """Add a number of months to a date."""
    month = date.month - 1 + number
    return update_month(date, month)

def update_month(date, month):
    """Create a new date with a modified number of months."""
    year = date.year + month / 12
    month = month % 12 + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return date.replace(year=year, month=month, day=day)

def add(date, key=None, amount=None, factor=1, use_localtime=None, force=False, **kwds):
    """Add time to the original moment."""
    if not key and not amount and len(kwds):
        items = iteritems(kwds)
    else:
        items = [(key, amount)]

    # TODO error (if not force) if time of day != 00:00:00 and using years, months, days
    # TODO use localtime for hours, minutes, seconds, milliseconds as default
    # add table to documentations

    # remember timezone
    tzinfo = date.tzinfo

    # normalize (just to be sure)
    date = tzinfo.normalize(date)

    # now we are working on utc (and localize back again later)
    date = date.replace(tzinfo=pytz.utc)

    for key, amount in items:
        if key == 'years' or key == 'year':
            date = add_month(date, amount * 12 * factor)
        elif key == 'months' or key == 'month':
            date = add_month(date, amount * factor)
        elif key == 'weeks' or key == 'week':
            date += timedelta(weeks=amount) * factor
        elif key == 'days' or key == 'day':
            date += timedelta(days=amount) * factor
        elif key == 'hours' or key == 'hour':
            date += timedelta(hours=amount) * factor
        elif key == 'minutes' or key == 'minute':
            date += timedelta(minutes=amount) * factor
        elif key == 'seconds' or key == 'second':
            date += timedelta(seconds=amount) * factor
        elif key == 'milliseconds' or key == 'millisecond':
            date += timedelta(milliseconds=amount) * factor
        elif key == 'microseconds' or key == 'microsecond':
            date += timedelta(microseconds=amount) * factor

    date = tzinfo.localize(date.replace(tzinfo=None), is_dst=None) # TODO is_dst
    return date

def replace(date, **kwds):
    """A Pythonic way to replace various date attributes."""
    for key, value in iteritems(kwds):
        if key == 'years' or key == 'year':
            date = date.replace(year=value)
        elif key == 'months' or key == 'month':
            date = date.replace(month=value)
        elif key == 'days' or key == 'day':
            date = date.replace(day=value)
        elif key == 'hours' or key == 'hour':
            date = date.replace(hour=value)
        elif key == 'minutes' or key == 'minute':
            date = date.replace(minute=value)
        elif key == 'seconds' or key == 'second':
            date = date.replace(second=value)
        elif key == 'microseconds' or key == 'microsecond':
            date = date.replace(microsecond=value)
        elif key == 'weekday':
            weekday = date.isoweekday()
            if value < 0:
                days = abs(weekday - value)
            else:
                days = weekday - value
            delta = date - timedelta(days)
            date = delta
    return date

