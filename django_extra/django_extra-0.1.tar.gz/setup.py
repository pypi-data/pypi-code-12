#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name="django_extra",
    version="0.1",
    packages=find_packages(),
    description="an extenstions of django",
    install_requires=['sshtunnel', 'django>=1.8'],
    author="DrWrong",
    author_email="yuhangchaney@gmail.com"
)
