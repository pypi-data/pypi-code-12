#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

import faz


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()

with open(path.join(here, 'HISTORY.rst'), encoding='utf8') as f:
    history = f.read().replace('.. :changelog:', '')

# requirements = [line.strip() for line in open("requirements.txt").readlines()]

test_requirements = [
    'coverage',
]

setup(
    name='faz',
    version=faz.__version__,
    description='"A Make-like tool with a syntax similar to Drake."',
    long_description=readme + '\n\n' + history,
    author=faz.__author__,
    author_email=faz.__email__,
    url=faz.__url__,
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    entry_points={
        'console_scripts': [
            'faz = faz.main:main',
        ]
    },
    include_package_data=True,
    install_requires=[
        'argparse==1.2.1',
        'decorator==3.4.0',
        'wheel==0.24.0'
        ],
    license="BSD",
    zip_safe=False,
    keywords='faz',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        # 'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
