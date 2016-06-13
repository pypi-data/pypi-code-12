#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

def tests ():
    from discover import DiscoveringTestLoader
    loader = DiscoveringTestLoader()
    suite = loader.discover("source/test/python", pattern="*.py")
    return suite

setup(
    name = "mentat",
    version = "1.0.1",
    author = "Corey D. Holland",
    author_email = "cholland1989@me.com",
    description = "Resource monitoring and alerts.",
    license = "Apache Software License",
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: System :: Monitoring",
        "Topic :: Utilities"
    ],
    packages = ["mentat"],
    package_dir = {"mentat":"source/main/python"},
    scripts = ["source/main/resources/mentat"],
    test_suite = "SETUP.tests",
    install_requires = ["argparse>=1.0", "discover>=0.4", "psutil>=4.0"],
    url = "https://github.com/cholland1989/mentat"
)