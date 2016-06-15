"""datetimeutil converts between different datetime related objects.

In this module, make sure we don't use the tzinfo
parameter in the constructor datetime.datetime. Instead,
always gets a timezone from pytz, then do localize (and
normalize after that).
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import re
import time

from dateutil import parser as dateutilparser
import pytz
import six
import tzlocal

ISO_FORMAT= "%Y-%m-%dT%H:%M:%S%z"
ISO_FORMAT_WITH_TZ_NAME = "%Y-%m-%dT%H:%M:%S%z%Z"

LOCAL_TIMEZONE = tzlocal.get_localzone()

# Mon Jan 2 15:04:05 -0700 MST 2006
_mst_timezone = pytz.timezone("US/Mountain")
GO_REFERENCE_TIME = _mst_timezone.normalize(
    _mst_timezone.localize(
        datetime.datetime(
            2006,
            1,
            2,
            15,
            4,
            5,
        )
    )
)

TIMESTAMP_REGEX = re.compile(r"((?<=\D)|^)(\d{10,19})((?=\D)|$)")

_timestamp_units = ["s", "ms", "us", "ns"]


def real_localize(dt, tz):
    """Attach timezone info to a datetime object.

    This is basically tz.normalize(tz.localize(dt))

    Args:
        dt: A datetime.
        tz: A pytz timezone.

    Returns:
        A datetime object which is a clone of the given dt, with the given
        timezone info attached.
    """
    return tz.normalize(tz.localize(dt))


def convert_timezone(dt, tz=LOCAL_TIMEZONE):
    """Converts a datetime object to a specific timezone.

    By default, the datetime object is converted into local timezone."""
    return tz.normalize(dt.astimezone(tz))


def datetime_to_timestamp(dt):
    """Converts datetime to a UNIX timestamp.

    Args:
        dt: A datetime. The datetime to be converted.

    Returns:
        An integer that represents the converted UNIX timestamp in seconds.
    """
    # time.mktime can only take local time, so need to convert
    # dt to local timezone first
    dt = convert_timezone(dt, tz=LOCAL_TIMEZONE)
    return time.mktime(dt.timetuple())


def timestamp_to_local_datetime(timestamp):
    """Converts timestamp to a datetime with local timezone info.

    Args:
        timestamp: An int. The UNIX timestamp in seconds to be converted.

    Returns:
        The converted datetime object with local timezone info.
    """
    dt = datetime.datetime.fromtimestamp(timestamp, LOCAL_TIMEZONE)
    return dt


def number_to_local_datetime(number):
    """Guesses the units of a timestamp.

    Args:
        number: An int. The number that is assumed to be a UNIX timestamp
            without units specified.

    Returns:
        A tuple of (datetime, str). The first element is the datetime object
        for the timestamp with local one info. The second element is the guessed
        unit, which can be s, ms, us, or ns. Raise ValueError if a valid
        conversion cannot be done.
    """
    i = 0
    n = number
    while n > 10 ** 10:
        n /= 1000
        i += 1
        if i >= len(_timestamp_units):
            raise ValueError("number %s is too big" % number)

    dt = datetime.datetime.fromtimestamp(n, LOCAL_TIMEZONE)
    return dt, _timestamp_units[i]


# A tuple of 2-tuple's. The first element of a 2-tuple is the format to match
# against a string to extract the datetime, the element is the conversion
# method that probably converts the datetime object to local time zone.
_COMMON_DATETIME_FORMATS_AND_LAMBDA = (
    # %z only works in Python 3.2 or later
    # (ISO_FORMAT, lambda dt: dt.astimezone(LOCAL_TIMEZONE)),
    # %z only works in Python 3.2 or later
    # (ISO_FORMAT_WITH_TZ_NAME, lambda dt: dt.astimezone(LOCAL_TIMEZONE)),
    (
        "%Y-%m-%dT%H:%M:%S.%fZ",
        lambda dt: dt.replace(tzinfo=pytz.utc).astimezone(LOCAL_TIMEZONE),
    ),
)

def guess_local_datetime(s):
    """Guesses the datetime for a given string.

    Args:
        s: A string. A date time with unspecified format.

    Returns:
        A datetime object for the given string in local time zone.

    Raises:
        ValueError if the string cannot be parsed as a datetime object.
    """
    for dt_format, func in _COMMON_DATETIME_FORMATS_AND_LAMBDA:
        try:
            func(datetime.datetime.strptime(s, dt_format))
        except ValueError:
            continue

    dt = dateutilparser.parse(s)
    if dt.tzinfo:
        return dt.astimezone(LOCAL_TIMEZONE)
    else:
        return LOCAL_TIMEZONE.localize(dt)


def strftime(format, mixed, localize=False):
    """Formats a time to a string.

    Just like time.strftime
    (https://docs.python.org/2/library/time.html#time.strftime) but this function
    can take different types of "time" object. It can take a timestamp in
    seconds, a datetime object, or a struct_time
    (https://docs.python.org/2/library/time.html#time.struct_time).

    If mixed is a datetime with a timezone, the result of strftime
    """
    dt = None
    if type(mixed) in six.integer_types or type(mixed) == float:
        dt = timestamp_to_local_datetime(mixed)
    elif type(mixed) == datetime.datetime:
        dt = mixed
    elif type(mixed) == time.struct_time:
        dt = timestamp_to_local_datetime(time.mktime(mixed))

    return dt.strftime(format)
