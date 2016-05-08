#!/usr/bin/env python
# -*- coding: utf-8 -*-
from os.path import join

from setuptools import setup


pkg = "dateslider"

# should be loaded below
__version__ = None

with open(join(pkg, '_version.py')) as version:
    exec(version.read())

with open('README.rst') as readme:
    README = readme.read()


setup(
    name=pkg,
    version=__version__,
    description="A date slider Jupyter widget",
    long_description=README,
    author="Nicholas Bollweg",
    author_email="nick.bollweg@gmail.com",
    license="BSD-3-Clause",
    url="https://github.com/bollwyvl/widget-dateslider",
    keywords="ipython jupyter blockly",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: IPython",
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License"
    ],
    packages=[pkg],
    setup_requires=["notebook"],
    tests_require=["nose", "requests", "coverage"],
    include_package_data=True
)
