#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from setuptools import setup, find_packages

setup(
    name='samitizer',
    version='0.1.6',
    license='MIT',
    author='Jamie Seol',
    author_email='theeluwin@gmail.com',
    url='https://github.com/theeluwin/samitizer',
    description='Python library and script for converting SAMI file',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['setuptools'],
    classifiers=[],
)
