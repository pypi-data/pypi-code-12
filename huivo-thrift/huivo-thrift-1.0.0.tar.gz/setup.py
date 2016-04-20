#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requires = [
    'thrift',
]


setup(
    name='huivo-thrift',
    description='huivo-thrift',

    version='1.0.0',
    packages=find_packages(),
)
