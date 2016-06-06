#!/usr/bin/env python

from distutils.core import setup

from setuptools import setup

setup(
    name="PhilUtils",
    use_vcs_version=True,
    description="Phil Zerull's tiny library of miscellaneous functions",
    author="Philip Zerull",
    author_email="przerull@gmail.com",
    packages=['philutils'],
    setup_requires=['hgtools'],
)
