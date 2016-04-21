# -*- coding: UTF-8 -*-
# lvjiyong on 2015/4/26.

import datetime
import time
import re


def get_time():
    # 获得当前时间
    now = datetime.datetime.now()
    # 转换为指定的格式:
    ftime = now.strftime("%Y-%m-%d %H:%M:%S")
    return ftime


def get_timestamp(ctime=None):
    """获取时间戳"""
    if ctime:
        return time2timestamp(ctime)
    else:
        return time.time()


def timestamp_tostring(stamp):
    if stamp is not None and re.compile('^[\d\.]+$').match(str(stamp)):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(stamp)))
    else:
        return stamp


def time_tostring(ctime=None):
    timestamp = get_timestamp(ctime)
    return timestamp_tostring(timestamp)


def time2timestamp(ctime=None):
    try:
        if isinstance(ctime, time.struct_time):
            timestamp = time.mktime(ctime)
        elif isinstance(ctime, str):
            timestamp = time.mktime(time.strptime(ctime, '%Y-%m-%d %H:%M:%S'))
        elif isinstance(ctime, int):
            timestamp = time.time() + ctime
        else:
            timestamp = time.time()
    except:
        timestamp = time.time()
    return timestamp