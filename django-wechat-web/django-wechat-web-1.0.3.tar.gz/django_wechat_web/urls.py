#!/usr/bin/env python
# coding=utf-8
# *************************************************
# File Name    : wechat/urls.py
# Author       : Cole Smith
# Mail         : tobewhatwewant@gmail.com
# Github       : whatwewant
# Created Time : 2016年04月19日 星期二 15时47分42秒
# *************************************************
from django.conf.urls import url

from .views import Wechat

urlpatterns = [
    url(r'^$', Wechat.as_view()),  
]
