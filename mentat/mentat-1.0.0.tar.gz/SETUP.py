#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools, unittest

def tests ():
    loader = unittest.TestLoader()
    suite = loader.discover("source/test/python", pattern="*.py")
    return suite

setuptools.setup(
    name = "mentat",
    version = "1.0.0",
    author = "Corey D. Holland",
    author_email = "cholland1989@me.com",
    description = "Resource monitoring and alerts.",
    license = "Apache Software License",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities"
    ],
    packages = ["mentat"],
    package_dir = {"mentat":"source/main/python"},
    scripts = ["source/main/resources/mentat"],
    test_suite = "SETUP.tests",
    install_requires = ["psutil==4.2.0"],
    url = "https://github.com/cholland1989/mentat"
)