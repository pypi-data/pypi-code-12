#!/usr/bin/env python

"""
distutilazy
-----------

Extra distutils commands.

:license: MIT, see LICENSE for more details.
"""

from __future__ import print_function

import os
import sys

try:
    import setuptools
    from setuptools import setup
except ImportError as exp:
    setuptools = None
    from distutils.core import setup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import distutilazy
import distutilazy.clean
import distutilazy.test

CLASSIFIERS = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.2",
    "Programming Language :: Python :: 3.3",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Archiving :: Packaging",
    "Topic :: System :: Systems Administration",
]

long_description = __doc__
with open(os.path.join(os.path.dirname(__file__), "README.rst")) as fh:
    long_description = fh.read()

params = dict(
    name = "distutilazy",
    author = "Farzad Ghanei",
    author_email = "farzad.ghanei@gmail.com",
    url = "http://github.com/farzadghanei/distutilazy/",
    packages = ["distutilazy", "distutilazy.command"],
    version = distutilazy.__version__,
    description = "Extra distutils commands",
    long_description = long_description,
    license = "MIT",
    classifiers = CLASSIFIERS,
    cmdclass = {
        "clean_pyc": distutilazy.clean.CleanPyc,
        "clean_jython_class": distutilazy.clean.CleanJythonClass,
        "clean_all": distutilazy.clean.CleanAll,
        "test": distutilazy.test.RunTests
        }
)

if setuptools:
    params.update(zip_safe = True)

dist = setup(**params)
