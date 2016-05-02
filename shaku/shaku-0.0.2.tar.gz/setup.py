#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: xiaoh
# Mail: xiaoh@about.me
# Created Time: 2016-05-03 02:14:30
#############################################

from setuptools import setup, find_packages
import shaku

def readme():
    return open("README.md").read()

setup(
    name = "shaku",
    version = shaku.__version__,
    keywords = ("xiaoh", "xingming", "shaku", "crontab", "service"),
    description = "Shaku 是一个脚本（命令等）定时执行的 WebService 框架，它提供了 RestAPI 来帮助开发人员更容易的将脚本设置成一个定时任务。",
    long_description = readme(),
    license = "MIT Licence",

    url = "https://pypi.python.org/pypi?:action=display&name=shaku",
    author = "xiaoh",
    author_email = "xiaoh@about.me",

    packages = ['shaku'],
    package_data = {
    },
    include_package_data = True,
    platforms = "any",
    install_requires = ["click", "requests"],

    scripts = ['bin/shaku']
#    entry_points = {
#        'console_scripts': [
#            'fcon = bin/fcon'
#        ]
#    }
)

