#!/usr/bin/env python2

from setuptools import setup

with open("README.md") as f:
    readme = f.read()

setup(name="callbackToReturnVal",
    version="0.1.1",
    description="Wrapper function that returns the value that is sent to a callback value as the value that the wrapper gives",
    long_description=readme,
    licence='MIT',
    author="Jeandre Le Roux",
    author_email="theblazehen@theblazehen.com",
    url="http://github.com/theblazehen/python-callbackToReturnVal",
    packages=['callbackToReturnVal'])
