#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import immutable_default_args


description = str("Very small package that offers a metaclass to automatically "
                  "safeguard mutable function arguments, preventing them from "
                  "being modified.")

setup(
    name='immutable_default_args',
    version='0.0.3',
    description=description,
    long_description=immutable_default_args.__doc__,
    author="Timm Wagener",
    author_email='wagenertimm@gmail.com',
    packages=find_packages(),
    zip_safe=False,
    test_suite='tests',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: Freely Distributable',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
