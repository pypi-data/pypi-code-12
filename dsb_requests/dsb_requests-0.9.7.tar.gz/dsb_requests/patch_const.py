#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-17 21:06:48
# Filename      : patch_const.py
# Description   : 
from __future__ import print_function, unicode_literals
from dsb_requests import _init
import inspect
import os

DEFAULT_OPTIONS = {
        'PROXY_RETRY'           :       '2',
        'REQUEST_RETRY'         :       '2',
        'REQUEST_RETRY_INTERVAL':       '0',
        'NODE_CACHE_COUNTER'    :       '10',
        'DSB_CLIENT_KEY'        :       '',
        }

def get_options():
    import os
    _options = DEFAULT_OPTIONS.copy()
    _options.update(_init.read_dsb_requests_init_data())
    for option_name in _options.keys():
        if option_name in os.environ:
            _options[option_name] = os.environ[option_name]

    return _options

if __name__ != "__main__":
    for context in inspect.stack()[1:]:
        frame = context[0]
        if frame.f_code.co_name == '<module>':
            frame.f_globals.update(get_options())
            break

