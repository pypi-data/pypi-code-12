#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="redis_logging_handler",
    version="0.1",
    packages=find_packages(),
    description="a redis log handler",
    install_requires=['redis'],
    author="DrWrong",
    author_email="yuhangchaney@gmail.com"
)
