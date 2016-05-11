#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-report',
    version='0.2.1',
    author='Brett Wandel',
    author_email='brett.wandel@live.com.au',
    maintainer='Brett Wandel',
    maintainer_email='brett.wandel@live.com.au',
    license='MIT',
    url='https://github.com/wandel/pytest-atom',
    description='Creates json report that is compatible with atom.io\'s linter message format ',
    long_description=read('README.rst'),
    packages=['pytest_report'],
    install_requires=['pytest>=2.9'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'report = pytest_report.plugin',
        ],
    },
)
