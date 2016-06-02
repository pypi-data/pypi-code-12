#!/usr/bin/env python
# coding=utf-8

import sys
from setuptools import setup, find_packages

import ordinaldate


requirements = []

python_version = sys.version_info
if python_version.major < 3 or python_version.minor < 4:
    requirements += ["enum34"]


setup(
    name="ordinaldate",
    version=ordinaldate.__version__,
    url="http://github.com/brianjbuck/ordinaldate/",
    download_url="https://github.com/brianjbuck/ordinaldate/tarball/1.0.0/",
    license="MIT Software License",
    author="Brian Buck",
    install_requires=requirements,
    author_email="brian@thebuckpasser.com",
    description="Python module to create dates based on the (first, second, third, etc) day of the week in a month",
    packages=find_packages(exclude=["*.tests"]),
    include_package_data=True,
    platforms="any",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Development Status :: 4 - Beta",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
