#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
from setuptools import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

# Use timestamp as version, we never need to keep track of anything then :)
VERSION=str(time.time())

setup(
    name='python-bogus-project-honeypot',
    version=VERSION,
    description="Useless bogus project honeypot",
    long_description=readme,
    author="Donald Trump's Hair",
    author_email='spam@overtag.dk',
    url='https://github.com/benjaoming/python-bogus-project-honeypot',
    packages=[
        'bogus_honeypot',
    ],
    include_package_data=True,
    license="MIT",
    zip_safe=False,
    keywords='spam, honeypot',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
