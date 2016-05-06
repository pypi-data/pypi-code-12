#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
easyXlsx setup.py
"""

from setuptools import setup, find_packages

__version__ = '0.2.9'

INSTALL_REQUIRES = ['XlsxWriter>=0.8.5']

setup(
    name='easyxlsx',
    version=__version__,
    author='tommao',
    packages=find_packages(),
    description='excel export component.',
    author_email='istommao@gmail.com',
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    zip_safe=False,
    license='http://opensource.org/licenses/MIT',
    url='https://github.com/istommao/easyXlsx'
)
