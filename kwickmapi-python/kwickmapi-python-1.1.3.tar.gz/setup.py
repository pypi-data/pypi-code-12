# -*- coding: utf-8 -*-
"""
Created on Sat Aug 22 02:35:48 2015

@author: bloodywing
"""

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

packages = [
    'kwick',
]

requires = [
    'requests',
]

test_requires = [
    'nose'
]

try:
    from unittest.mock import Mock
except ImportError:
    test_requires.append('mock')

here = os.path.dirname(os.path.abspath(__file__))
f = open(os.path.join(here, 'README.md'))
long_description = f.read().strip()
f.close()

setup(
    name='kwickmapi-python',
    version='1.1.3',
    description='A python library for kwick.de based on their mapi',
    long_description=long_description,
    url='https://github.com/bloodywing/kwickmapi-python',
    packages=packages,
    install_requires=requires,
    requires=requires,
    tests_require=test_requires,
    test_suite = 'nose.collector',
    author='Bloodywing',
    author_email='bloodywing@tastyespresso.de',
    license='GPL 3.0',
    keywords=['kwick', 'api', 'socialmedia', 'website', 'library']
)
