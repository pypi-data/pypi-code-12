#!/usr/bin/env python3

from setuptools import setup, find_packages


setup(
    name="pd2hts",
    version="0.1.1",
    license="GPL3",
    description=("Read and write Pandas objects from/to Hydrognomon "
                 "timeseries files"),
    author="Antonis Christofides",
    author_email="antonis@antonischristofides.com",
    url="https://github.com/openmeteo/pd2hts",
    packages=find_packages(),
    install_requires=['pandas>=0.14'],
    test_suite="tests",
    tests_require=['iso8601'],
)
