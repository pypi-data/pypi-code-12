#!/usr/bin/python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Copyright (C) 2015-2016 Jan Mach <honza.mach.ml@gmail.com>
# Use of this source is governed by the MIT license, see LICENSE file.
#-------------------------------------------------------------------------------

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
    
setup(
    name = 'pydgets',
    version = '0.4',
    description = 'Console widget library for Python 3',
    long_description = long_description,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Environment :: Console',
    ],
    keywords = 'library console widgets',
    url = 'https://github.com/honzamach/pydgets',
    author = 'Jan Mach',
    author_email = 'email@jan-mach.cz',
    license = 'MIT',
    packages = ['pydgets'],
    include_package_data = True,
    zip_safe = False
)
