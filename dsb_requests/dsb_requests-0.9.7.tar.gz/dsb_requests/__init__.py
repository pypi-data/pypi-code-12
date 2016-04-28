#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-17 11:09:25
# Filename      : __init__.py
# Description   : 
from __future__ import print_function, unicode_literals

from ._requests import (request, get, post, delete, put, flush_ip)
import requests

session = requests.session

