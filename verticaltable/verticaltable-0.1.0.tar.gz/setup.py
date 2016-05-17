#!/usr/bin/env python
# coding: utf-8
from setuptools import setup
from verticaltable import __author__, __version__, __license__

setup(
    name='verticaltable',
    version=__version__,
    description='VERTICALTABLE structured text parser',
    license=__license__,
    author=__author__,
    author_email='ytyng@live.jp',
    url='https://github.com/ytyng/verticaltable.git',
    keywords='Python, Data structure',
    packages=['verticaltable'],
    entry_points={
    },
)
