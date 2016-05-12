#!/bin/env python
#-*- encoding=utf8 -*-
import json
import urllib
import hashlib
from datetime import datetime, date
from time import struct_time, strftime
import sys
import random
import base64

"""
使用方法:
    from nwbase_utils import util

    util.MyJSONEncoder.encode(some_obj)
"""


class _MyJSONEncoder(json.JSONEncoder):
    """JSON编码器，为默认的json编码器增加datetime类型支持
    """
    def default(self, obj):
        if isinstance(obj, struct_time):
            return strftime('%Y%m%d%H%M%S', obj)
        elif isinstance(obj, datetime):
            return obj.strftime('%Y%m%d%H%M%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y%m%d')
        else:
            return json.JSONEncoder.default(self, obj)

MyJSONEncoder = _MyJSONEncoder()


class TEnum:
    """枚举类，增加枚举类型支持"""
    def __init__(self, arguments):
        self._keys = []
        self._vals = []
        idx = 0
        val = idx
        for name in arguments:
            if arguments[name] is None:
                val = idx
            else:
                val = arguments[name]
            self._keys.append(name)
            self._vals.append(val)
            setattr(self, name.strip(), val)
            idx = idx + 1

    def has_key(self, key_):
        return (key_ in self._keys)

    def has_val(self, val_):
        return (val_ in self._vals)


def list_to_dict(list_, key=None):
    """序列转换为字典
    """
    res = {}
    index = 0
    for eachItem in list_:
        if key is None:
            res[index] = eachItem
            index += 1
        else:
            res[eachItem[key]] = eachItem
    return res


class ConfigObj(object):
    pass

def parser_config(module_):
    """将模块转换为对象返回
    """
    all_config = module_.__dict__
    res = ConfigObj()
    for each_key in all_config:
        each_val = all_config[each_key]
        if each_key.startswith('_'):
            continue
        if isinstance(each_val, dict):
            inner_config = ConfigObj()
            for each_inner_key in each_val:
                setattr(inner_config, each_inner_key, each_val[each_inner_key])
            setattr(res, each_key, inner_config)
        else:
            setattr(res, each_key, all_config[each_key])
    return res

def get_log_session(tornado_ins):
    """获取log日志的session
    """
    return tornado_ins.request.headers.get('X-Log-Session', '0')


def get_real_ip(tornado_ins):
    """获取真实ip地址
    """
    return tornado_ins.request.headers.get('X-Real-Ip', '0')


def now():
    """ 获取当前时间(datetime.datetime.now())
    """
    return datetime.now()


def now_stamp():
    """ 获取当前时间戳（yyyymmddHHMMss格式）
    """
    return now().strftime("%Y%m%d%H%M%S")


def singleton(cls, *args, **kw):
    """
    单例类的 decorator
    使用方法:
        import util

        #单例化
        @util.singleton
        class MyClass:
            def __init__(self, arg):
            pass

        obj1 = MyClass()
        obj2 = MyClass()

        # 同一个单例
        obj1 == obj2

    """
    instances = {}   
    def _singletonize(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]
    return _singletonize


def dec2bin(cls, string_num):
    """十进制转2进制
    """
    num = int(string_num)
    mid = []
    base = [str(x) for x in range(10)] + [ chr(x) for x in range(ord('A'), ord('A')+6)]
    while True:
        if num == 0: break
        num, rem = divmod(num, 2)
        mid.append(base[rem])
    return ''.join([str(x) for x in mid[::-1]])


def cal_str_length(str_data):
    """
    计算字符串的长度
    中文字符长度为2
    西文字符长度为1
    """
    if not isinstance(str_data, unicode):
        str_data = cls.encode_to_unicode(str(str_data))
    length = 0
    for w in str_data:
        if len(str([w])) < 8:
            length += 1
        else:
            length += 2
    return length


def urldecode(query):
    """url解码，string -> dict
    """
    d = {}
    a = query.split('&')
    for s in a:
        if s.find('=') >= 0:
            k, v = map(urllib.unquote, s.split('='))
            d[k] = v
    return d


def is_deep_key_exists(obj, *keys):
    """判断字典嵌套的key是否存在，如判断 data['a']['b']['c']['d'] 是否存在，则调用 is_deep_key_exists(data, 'a', 'b', 'c', 'd')
    """
    current_obj = obj
    for each_key in keys:
        if each_key not in current_obj:
            return False
        else:
            current_obj = current_obj[each_key]
    return True
