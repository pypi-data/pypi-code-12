# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "Token"
VERSION = "1.6.4"



# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.10", "six >= 1.9", "certifi", "python-dateutil", "ed25519"]

setup(
    name=NAME,
    version=VERSION,
    description="Token client to REST Apis",
    author="Mariano Sorgente",
    author_email="mariano.sorgente@token.io",
    keywords=["Swagger", "Token API"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Interact with Token REST Apis
    """
)
