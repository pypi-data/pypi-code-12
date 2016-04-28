#!/usr/bin/env python
#coding:utf-8
# Author        : tuxpy
# Email         : q8886888@qq.com.com
# Last modified : 2016-03-17 17:57:21
# Filename      : setup.py
# Description   : 
from setuptools import setup

setup(
        name = 'dsb_requests',
        version = '0.9.7',
        author = 'tuxpy',
        include_package_data = True,
        packages = [
            'dsb_requests',
            ],
        install_requires = ['requests', 'lxml', 'mock'],
        description = 'duoshoubang \'s requests',
        scripts = ['bin/dsb_requests'],
        )

