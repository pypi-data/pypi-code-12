#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from setuptools import setup

def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read()

setup(
    name = "modulemd",
    version = "0.1",
    author = "Petr Šabata",
    author_email = "contyk@redhat.com",
    description = ("A python3 library for manipulation of the proposed "
        "module metadata format."),
    license = "MIT",
    keywords = "modularization,modularity,module,metadata",
    url = "https://pagure.io/fm-metadata",
    packages = ["modulemd", "tests"],
    long_description = read("README.rst"),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
    ],
    test_suite = "tests",
    install_requires = [
        "PyYAML",
        ],
)
