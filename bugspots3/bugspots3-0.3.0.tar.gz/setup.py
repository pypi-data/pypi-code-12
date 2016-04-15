#!/usr/bin/env python3

# -*- encoding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 textwidth=79

from setuptools import setup

import bugspots

setup(
    name="bugspots3",
    version=bugspots.__version__,
    description=bugspots.__doc__,
    author=bugspots.__author__,
    author_email="support@gitmate.io",
    url="https://gitlab.com/gitmate/bugspots3",
    py_modules=["bugspots"],
    scripts=["bugspots.py"],
    license=bugspots.__license__,
    platforms="Unix",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Software Development :: Bug Tracking",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities"])
