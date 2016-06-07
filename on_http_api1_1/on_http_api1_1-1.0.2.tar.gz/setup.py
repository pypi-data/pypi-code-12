# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "on_http_api1_1"
VERSION = "1.0.2"



# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.10", "six >= 1.9", "certifi", "python-dateutil"]

setup(
    name=NAME,
    version=VERSION,
    description="Monorail API",
    author_email="",
    url="",
    keywords=["Swagger", "Monorail API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Monorail CI core API
    """
)


