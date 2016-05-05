# coding:utf-8
# Copyright (C) Alibaba Group

"""
edas-detector.common : 
"""

__author__ = "Thomas Li <yanliang.lyl@alibaba-inc.com>"
__license__ = "GNU License"

from edsd import __version__

from datetime import datetime


def isodt2ts(s):
    """convert a date time string to a unix timestamp.

    :param s: date time string
    :return:
    """
    fmts = ['%Y-%m-%d %H:%M:%S,%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S']
    s = s.strip() if s else s
    for fmt in fmts:
        try:
            dt = datetime.strptime(s, fmt)
            return timedelta2ts(dt - datetime.fromtimestamp(0))
        except:
            continue

    return 0


def timedelta2ts(d):
    DAY = 24 * 60 * 60
    if not d:
        return 0

    return d.days * DAY + d.seconds

