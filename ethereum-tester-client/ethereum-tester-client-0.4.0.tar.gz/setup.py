#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup


DIR = os.path.dirname(os.path.abspath(__file__))

version = '0.4.0'

readme = open(os.path.join(DIR, 'README.md')).read()


setup(
    name='ethereum-tester-client',
    version=version,
    description="""Ethereum JSON RPC Client for testing""",
    long_description=readme,
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/pipermerriam/ethereum-tester-client',
    include_package_data=True,
    py_modules=['eth_tester-client'],
    install_requires=[
        "ethereum>=1.3.6",
        "gevent>=1.1.1",
    ],
    license="MIT",
    zip_safe=False,
    keywords='ethereum',
    packages=[
        "eth_tester_client",
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
