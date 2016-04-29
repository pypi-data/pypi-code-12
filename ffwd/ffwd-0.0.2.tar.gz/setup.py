#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

import ffwd

NAME = "ffwd"
VERSION = str(ffwd.VERSION)

req = "requirements.txt"

with open(req) as f:
    required = f.read().splitlines()

setup(
    name=NAME,
    version=VERSION,
    description="A Python client for FFWD",
    author=["John-John Tedro"],
    author_email=["udoprog@tedro.se"],
    license="Apache 2.0",
    packages=["ffwd"],
    scripts=["bin/ffwd-send"],
    install_requires=required,
    test_suite = 'nose.collector',
)
