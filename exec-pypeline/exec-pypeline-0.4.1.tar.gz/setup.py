#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of exec-pypeline.
# https://github.com/rfloriano/pypeline

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Rafael Floriano da Silva rflorianobr@gmail.com


from setuptools import setup, find_packages
from exec_pypeline import __version__

tests_require = [
    'mock',
    'nose',
    'nose-focus',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
    'sphinx',
]

setup(
    name='exec-pypeline',
    version=__version__,
    description='an incredible python package',
    long_description='''
an incredible python package
''',
    keywords='',
    author='Rafael Floriano da Silva',
    author_email='rflorianobr@gmail.com',
    url='https://github.com/rfloriano/pypeline',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Unix',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Operating System :: OS Independent',
    ],
    packages=find_packages(),
    include_package_data=False,
    install_requires=[
        # add your dependencies here
        # remember to use 'package-name>=x.y.z,<x.y+1.0' notation (this way you get bugfixes)
    ],
    extras_require={
        'tests': tests_require,
    },
    entry_points={
        'console_scripts': [
            # add cli scripts here in this form:
            # 'pypeline=pypeline.cli:main',
        ],
    },
)
