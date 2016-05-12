# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ""

setup(
    name="aliyun-python-sdk-emr-hack",
    version="0.1.2",
    description="A pip package",
    license="MIT",
    author="Liwen",
    packages=find_packages(exclude=["tests*"]),
    install_requires=['aliyun-python-sdk-core-emr-hack'],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
    ]
)
