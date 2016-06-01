#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='swissdict',
    version='0.0.1',
    packages=['swissdict'],
    requires=['python (>= 2.7)'],
    description='implementation of a multifunctional dict',
    long_description=open('README.rst').read(),
    author='Vasiliy Sinyurin',
    author_email='vasiliy@sinyur.in',
    url='https://github.com/war1or/swissdict',
    download_url='https://github.com/war1or/swissdict/tarball/master',
    license='MIT License',
    keywords='dict',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
