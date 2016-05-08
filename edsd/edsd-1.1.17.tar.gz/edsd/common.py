# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.common : 
"""
import os

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"

from edsd import __version__

from datetime import datetime, date


EDAS_DIRECTORY = '/tmp/edas-collect'


def isodt2ts(s):
    """convert a date time string to a unix timestamp.

    :param s: date time string
    :return: a unix timestamp, return 0 if any of the defined datetime formats
    are fail to match the given string.
    """
    fmts = ['%Y-%m-%d %H:%M:%S,%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S'
            '%m-%d-%Y %H:%M:%S',
            '%d-%m-%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%m/%d/%Y %H:%M:%S']

    s = s.strip() if s else s

    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return timedelta2ts(dt)
        except:
            continue

    return 0


def timedelta2ts(d):
    d = d - datetime.fromtimestamp(0) if isinstance(d, datetime) else d

    DAY = 24 * 60 * 60
    if not d:
        return 0

    return d.days * DAY + d.seconds


def todaystime(timestring):
    """ Convert a time format string(HH:MM:SS) to a unix timestamp, combined date
    with today, e.g:

    >>> todaystime('22:11:00') # today is 2016/05/07
    1462629611

    :param timestring: a formated timestring
    :return: unix timestamp
    """
    try:
        dt = datetime.strptime(timestring, '%H:%M:%S')
        td = date.today()  # today
        dt = datetime.combine(td, dt.time())

        return timedelta2ts(dt)
    except:
        return 0


def today_in_str():
    return datetime.now().strftime('%Y-%m-%d')


def ensure_dir(d):
    if os.path.isdir(d):
        return

    pd = os.path.dirname(d)
    ensure_dir(pd)

    # double check, no harm, but safer.
    if os.path.isdir(d):
        return
    os.mkdir(d)


def ensure_file(f):
    if os.path.isfile(f):
        return

    os.mknod(f)