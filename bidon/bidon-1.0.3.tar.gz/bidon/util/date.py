"""This module implements a wrapper around the standard library date and time functions to simplify
the parsing of ISO8601 date strings.
"""
import itertools
import re
from datetime import datetime, date, time, timezone


def local_now():
  """Returns a datetime object for the current time, timezone unaware."""
  return datetime.now()


def utc_now():
  """Returns a datetime object for the current time, with the tzinfo set to timezone.utc"""
  return datetime.utcnow().replace(tzinfo=timezone.utc)


def parse_date(val, fmt=None):
  """Returns a date object parsed from :val:.

  :param val: a string to be parsed as a date
  :param fmt: a format string, a tuple of format strings, or None. If None a
              built in list of format strings will be used to try to parse the
              date.
  """
  if isinstance(val, date):
    return val
  else:
    return parse_datetime(val, fmt).date()


def parse_time(val, fmt=None):
  """Returns a time object parsed from :val:.

  :param val: a string to be parsed as a time
  :param fmt: a format string, a tuple of format strings, or None. If None a built in list of format
              strings will be used to try to parse the time.
  """
  if isinstance(val, time):
    return val
  else:
    return parse_datetime(val, fmt).time()


def parse_datetime(val, fmt=None):
  """Returns a datetime object parsed from :val:.

  :param val: a string to be parsed as a date
  :param fmt: a format string, a tuple of format strings, or None. If None a built in list of format
              strings will be used to try to parse the date.
  """
  if isinstance(val, datetime):
    return val
  else:
    return _parse_datetime(_normalize_tz(str(val)), fmt)


def _parse_datetime(val, fmt=None):
  """Returns a datetime object parsed from :val:. The timezone, if any, on the
  string must be in the format that python can parse.

  :param val: a string to be parsed as a date
  :param fmt: a format string, a tuple of format strings, or None. If None a built in list of format
              strings will be used to try to parse the datetime.
  """
  if fmt is None:
    fmt = _DEFAULT_FORMATS

  if isinstance(fmt, str):
    return datetime.strptime(val, fmt)
  else:
    for opt in fmt:
      try:
        return _parse_datetime(val, opt)
      except ValueError:
        continue
    raise ValueError("Unable to parse string '{}' as a timestamp".format(val))


def _normalize_tz(val):
  """Normalizes all valid ISO8601 time zone variants to the one python will
  parse.

  :val: a timestamp string without a timezone, or with a timezone in one of the ISO8601 accepted
        formats.
  """
  match = _TZ_RE.match(val)
  if match:
    ts, tz = match.groups()
    if len(tz) == 5:
      # If the length of the tz is 5 then it is of the form (+|-)dddd, which is exactly what python
      # wants, so just return it.
      return ts + tz
    if len(tz) == 6:
      # If the length of the tz is 6 then it is of the form (+|-)dd:dd, just remove the colon
      return ts + tz[:3] + tz[4:]
    if tz == "Z" or tz == "z":
      # If the tz is "Z" or 'z', return a timezone of +0000
      return ts + "+0000"
    else:
      # Otherwise, the timzone must be of the format (+|-)dd, in which case we just need to add two
      # "0" to it, and it will be in the proper format.
      return ts + tz + "00"
  else:
    return val


def _join_date_and_time(dates, times, joiner):
  """Returns a tuple of all date and time format strings joined together by
  :joiner:.

  :dates: an enumerable of date format strings
  :times: an enumerable of time format strings
  :joiner: a string to join a date and time format together
  """
  return tuple("{}{}{}".format(d, joiner, t) for (d, t) in itertools.product(dates, times))


# A timezone can be one of:
# (+|-)dd, (+|-)dddd, (+|-)dd:dd, Z
_TZ_RE = re.compile(r"^(.*)((?:\+|-)\d\d(?::?\d\d)?|Z)$", re.IGNORECASE)

_DATE_FORMATS = (
  "%Y-%m-%d",
  "%Y%m%d")

_TIME_FORMATS_24_DELIM = (
  "%H:%M",
  "%H:%M:%S",
  "%H:%M:%S.%f")

_TIME_FORMATS_24_NODELIM = (
  "%H%M",
  "%H%M%S",
  "%H%M%S.%f")

_TIME_FORMATS_12 = (
  "%I:%M %p",
  "%I:%M:%S %p",
  "%I:%M:%S.%f %p")

_TIME_FORMATS = _TIME_FORMATS_24_DELIM \
                + _TIME_FORMATS_24_NODELIM \
                + _TIME_FORMATS_12 \
                + _join_date_and_time(_DATE_FORMATS, _TIME_FORMATS_24_DELIM, " ") \
                + _join_date_and_time(_DATE_FORMATS, _TIME_FORMATS_24_DELIM, "T") \
                + _join_date_and_time(_DATE_FORMATS, _TIME_FORMATS_24_NODELIM, "") \
                + _join_date_and_time(_DATE_FORMATS, _TIME_FORMATS_24_NODELIM, "T")

_DEFAULT_FORMATS = _DATE_FORMATS \
                   + _TIME_FORMATS \
                   + tuple("{}%z".format(f) for f in _TIME_FORMATS)
