# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Time zone conversion functionality
"""
import calendar
from datetime import datetime


def utc_to_local(utc_string):
    utc = datetime.strptime(utc_string, "%a, %d %b %Y %H:%M:%S GMT")
    local_timestamp = calendar.timegm(utc.timetuple())
    local_time = datetime.fromtimestamp(local_timestamp)
    formatted_time = local_time.strftime("%Y-%m-%d %H:%M:%S %Z").rstrip()
    return formatted_time
