# -*- encoding: utf-8 -*-

import re
import pytz
from datetime import datetime
from six import string_types

from .mystrptime import mystrptime

def get_timezone(timezone):
    if timezone == None:
        timezone = pytz.utc # default
    elif isinstance(timezone, string_types):
        timezone = pytz.timezone(timezone)
    return timezone

def guess_formula(date):
    if re.match(r'.*:[0-9]{2}[+-]', date):
        # seems to have a timezone offset
        formula = '%Y-%m-%d %H:%M:%S%z'

    elif re.match(r'.*:[0-9\.]+[+-]', date):
        # seems to have milliseconds/microseconds and timezone offset
        formula = '%Y-%m-%d %H:%M:%S.%f%z'

    # support for complete dates
    elif ":" in date:
        formula = '%Y-%m-%d %H:%M:%S'
    else:
        formula = "%Y-%m-%d"

    return formula

def parse_date(date, formula=None, timezone=None, is_dst=None):

    if isinstance(date, string_types):
        # support for complete dates with timezone
        if not formula:
            formula = guess_formula(date)

        # the follwing special handling is only neccessary, because
        # we need %z for timezone offeset
        # TODO with python3.2 this won't be neccessary !!!

        date = mystrptime(date, formula)

    # this is like the default handling
    elif isinstance(date, list) or isinstance(date, tuple):
        if len(date) == 1:
            # Python datetime needs the month and day, too.
            date = [date[0], 1, 1]
        date = datetime(*date)
    else:
        # this is already a datetime
        if date.tzinfo and (timezone == None):
            # if it has a timezone info we take this as default instead of utc
            timezone = date.tzinfo

    timezone = get_timezone(timezone)

    if formula and formula.endswith('%z'):
        # a date with timezone is parsed as UTC - so we can convert it to local timezone
        return date.replace(tzinfo=pytz.utc).astimezone(timezone)
    elif date.tzinfo:
        # already has a timezone (e.g. if a datetime with tz is supplied)
        return date.astimezone(timezone)

    # the date was in local timezone
    return timezone.localize(date, is_dst=is_dst)

