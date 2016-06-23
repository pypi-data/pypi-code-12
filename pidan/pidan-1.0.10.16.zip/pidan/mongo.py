# -*- coding: utf-8 -*-
#与mongodb相关的函数
import time

def timestamp_from_objectid(objectid):
    '''将时间戳转换成objectid'''
    result = 0
    try:
        result = time.mktime(objectid.generation_time.timetuple())
    except:
        pass
    return result