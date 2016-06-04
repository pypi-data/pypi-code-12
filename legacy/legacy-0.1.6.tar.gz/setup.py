#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import setuptools

setuptools.setup(
    name = "legacy",
    version = "0.1.6",
    author = "Hive Solutions Lda.",
    author_email = "development@hive.pt",
    description = "Legacy Support",
    license = "Apache License, Version 2.0",
    keywords = "legacy utils python",
    url = "http://legacy.hive.pt",
    zip_safe = False,
    py_modules = [
        "legacy"
    ],
    package_dir = {
        "" : os.path.normpath("src")
    },
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)
