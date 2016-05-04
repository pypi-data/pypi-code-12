# -*- coding: utf-8 -*-
# !/usr/bin/env python

from apysignature import __version__
from setuptools import setup, find_packages


setup(
    name='apysignature',
    version=__version__,
    install_requires=[
        'ordereddict>=1.1'
    ],
    url='https://github.com/erickponce/apysignature',
    description='Python implementation of the Ruby Signature library (https://github.com/mloughran/signature)',
    long_description=open("README.md").read(),
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries',
    ],
    author='Erick Ponce Leão',
    author_email='erickponceleao@gmail.com'
)
