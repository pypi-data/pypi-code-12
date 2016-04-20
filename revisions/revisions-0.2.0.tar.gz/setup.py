#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Revisions

import sys
import os

from setuptools import setup, Extension

setup_args = {
  'name': 'revisions',
  'version': '0.2.0',
  'author': 'Prashant Sinha',
  'author_email': 'prashant@ducic.ac.in',
  'url': 'https://github.com/PrashntS/revisions',
  'license': 'MIT',
  'description': 'Mock Python Requests with versioned cache control.',
  'packages': ['revisions'],
  'classifiers': [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Testing',
  ]
}

setup(**setup_args)
