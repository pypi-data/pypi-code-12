#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# vim: fenc=utf-8 ts=2 et sw=2 sts=2
#
# Copyright © 2016 Mohammad Amin Sameti <mamins1376@gmail.com>
#
# Distributed under terms of the GNU General Public License v3 license.

"""
setup PyBehnevis
"""

from setuptools import setup, find_packages

with open('README','r') as f:
  readme = f.read()

setup(
  name='pybehnevis',
  version='0.1.1',
  description='python wrapper for Behnevis API',
  long_description=readme,
  author='Mohammad Amin Sameti',
  author_email='mamins1376@gmail.com',
  url='https://github.com/mamins1376/PyBehnevis/',
  license='GNU General Public License v3 or later',
  keywords = 'pybehnevis api wrapper python3',
  packages=find_packages(),
  classifiers = [
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Topic :: Software Development',
    'Topic :: Internet :: WWW/HTTP',
    'Programming Language :: Python :: 3',
    'Operating System :: OS Independent',
    'Development Status :: 4 - Beta'
    ]
)

