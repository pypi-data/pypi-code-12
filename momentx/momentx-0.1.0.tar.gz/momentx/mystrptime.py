# -*- encoding: utf-8 -*-
"""
 strptime with with timezone offset (%z) support for python2.7

 support timezone offset (%z) with strptime
 from python 3.2 this is supported natively
 pylint:disable=super-init-not-called

"""

import datetime
import pytz

# pylint:disable=super-init-not-called
class OffsetTime(pytz.tzinfo.StaticTzInfo):
    def __init__(self, offset):
        """A dumb timezone based on offset such as +0530, -0600, etc.
        """
        hours = int(offset[:3])
        minutes = int(offset[0] + offset[3:])
        self._utcoffset = datetime.timedelta(hours=hours, minutes=minutes)
# pylint:enable=super-init-not-called

def mystrptime(value, fmt='%Y-%m-%d %H:%M:%S%z'):
    if fmt.endswith('%z'):
        fmt = fmt[:-2]
        offset = value[-5:]
        value = value[:-5]
        return OffsetTime(offset).localize(datetime.datetime.strptime(value, fmt)).astimezone(pytz.utc).replace(tzinfo=None)

    return datetime.datetime.strptime(value, fmt)

