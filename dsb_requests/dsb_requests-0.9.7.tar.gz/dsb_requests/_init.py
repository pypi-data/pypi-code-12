#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-21 09:05:56
# Filename      : _init.py
# Description   : 
from __future__ import print_function, unicode_literals
import os
import json

__ALL__ = ['init_dsb_requests']

CFG_PATH = os.path.join(os.path.expandvars('$HOME'), '.dsb_requestsrc')

def read(prompt, default = None):
    while True:
        line = raw_input(prompt).strip()
        if line:
            return line

        elif default is not None:
            return default
        

def init_dsb_requests():
    api_hostname = read('please enter api hostname:')
    api_port = int(read('please enter api port(default 16227):', 16227))
    dsb_client_key = read('please enter dsb client key:')
    with open(CFG_PATH, 'wb') as fd:
        fd.write(json.dumps({
            'API_HOSTNAME'      :       api_hostname,
            'API_PORT'          :       api_port,
            'DSB_CLIENT_KEY'    :       dsb_client_key,
            }))

def read_dsb_requests_init_data():
    if not os.path.exists(CFG_PATH):
        return {}

    with open(CFG_PATH, 'rb') as fd:
        return json.loads(fd.read())

