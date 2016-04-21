#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-17 11:19:15
# Filename      : logs.py
# Description   : 
from __future__ import print_function, unicode_literals
import logging
import sys

def print_error(error):
    logging.error(error)

def alert_error(error):
    print_error(error)
    sys.exit(-1)

def debug(msg):
    logging.debug(msg)

