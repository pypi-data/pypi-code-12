#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
try:
    import os
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='exvocabulary',
    version='0.0.1',
    author='Chen, Shang-Kuei',
    author_email='adavis10006@gmail.com',
    description=
    "Module to get part_of_speech, synonym, antonym, vocabulary_example, and hyphenation for a given word. Extend from Vocabulary",
    #long_description=long_description,
    url='https://github.com/adavis10006/ExVocabulary',
    license='MIT',
    install_requires=[
        "requests==2.8.1",
    ],
    ### adding package data to it
    packages=find_packages(exclude=['contrib', 'docs']),
    ###https://github.com/adavis10006/ExVocabulary/tarball/master
    download_url = 'https://github.com/adavis10006/ExVocabulary/tarball/master',
    #classifiers = [
    #    'Intended Audience :: Developers',
    #    'License :: OSI Approved :: MIT License',
    #    'Natural Language :: English',
    #    'Programming Language :: Python',
    #    'Programming Language :: Python :: 2.7',
    #    'Programming Language :: Python :: 3',
    #    'Programming Language :: Python :: 3.4',
    #],
    test_suite='tests',
    keywords=['Dictionary', 'Vocabulary', 'simple dictionary', 'pydict',
              'dictionary module'])
