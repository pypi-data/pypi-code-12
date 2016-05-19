# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "PureCloudPlatformApiSdk"
VERSION = "0.9.0.53"



# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil"]

setup(
    name="PureCloudPlatformApiSdk",
    version="0.9.0.53",
    description="PureCloud Platform API SDK",
    author="Interactive Intelligence, Inc.",
    author_email="DeveloperEvangelists@inin.com",
    url="https://developer.mypurecloud.com/api/rest/client-libraries/python/latest/",
    keywords=["Swagger PureCloud Platform API ININ Interactive Intelligence"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="A python package to interface with the PureCloud Platform API"
)


