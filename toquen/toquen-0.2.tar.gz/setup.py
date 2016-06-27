#!/usr/bin/env python
from setuptools import setup, find_packages
from toquen import version

setup(
    name="toquen",
    version=version,
    description="Python lib for Toquen: Joins Capistrano + AWS + Chef-Solo into small devops ease",
    author="Brian Muller",
    author_email="bamuller@gmail.com",
    license="MIT",
    url="http://github.com/bmuller/toquen-python",
    packages=find_packages(),
    requires=["boto3"],
    install_requires=["boto3>=1.3.1"]
)
