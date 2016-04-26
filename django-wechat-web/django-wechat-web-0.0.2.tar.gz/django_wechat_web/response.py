#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : response.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年04月20日 星期三 14时42分02秒
# *************************************************
import json

from django.http import HttpResponse

def Response(data):
    return HttpResponse(json.dumps(data))
