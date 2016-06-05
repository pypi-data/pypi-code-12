#!/usr/bin/env python3

import collections
import datetime
import time
from . import __version__


DEFAULT_USER_AGENT = 'python-haiker/{0}'.format(__version__)


def removed_dict(dic, keys):
    """Create a copy of dic, remove keys and return it."""
    return {kw: dic[kw] for kw in dic if kw not in keys}


def strftime(date, date_format):
    """Return a string expession of date.  This function is
    like date.strftime(date_format) but adjusts the timezone
    to UTC.
    """
    try:
        date = date.astimezone(datetime.timezone.utc)
    except ValueError:
        date = time.gmtime(time.mktime(date.timetuple()))
        return time.strftime(date_format, date)
    return date.strftime(date_format)


def serialize(obj, *, charset='utf-8',
              date_format='%a, %d %B %Y %H:%M:%S GMT'):
    """Return a string expression of obj."""
    if obj is None:
        return None
    if isinstance(obj, int):  # bool is a subclass of int
        obj = str(int(obj))
    if isinstance(obj, datetime.datetime):
        obj = strftime(obj, date_format)
    if isinstance(obj, str):
        obj = obj.encode(charset)
    if isinstance(obj, bytes):
        return obj
    if isinstance(obj, collections.Iterable):
        return b','.join(b'' if d is None else serialize(d) for d in obj)
    raise TypeError('{0!r} is an unsupported type'.format(type(obj)))


def build_params(params):
    """Return a list of (key, serialized value) pairs from params."""
    if params is None:
        return None
    if isinstance(params, collections.Mapping):
        return [(key, serialize(params[key])) for key in params]
    return [(key, serialize(value)) for key, value in params]
