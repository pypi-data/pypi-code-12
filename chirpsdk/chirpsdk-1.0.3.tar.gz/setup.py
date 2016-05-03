#!/usr/bin/env python

#------------------------------------------------------------------------
#
#  This file is part of the Chirp Python SDK.
#  For full information on usage and licensing, see http://chirp.io/
#
#  Copyright (c) 2011-2016, Asio Ltd.
#  All rights reserved.
#
#------------------------------------------------------------------------

from setuptools import setup, find_packages


setup(
    name = 'chirpsdk',
    version = '1.0.3',
    description = 'Chirp Python SDK',
    long_description = 'The Chirp Python SDK enables the user to create, send and query chirps, using the Chirp audio protocol.',
    license = 'Apache 2.0 for non-commercial use, commercial licenses apply for commercial use.',
    author = 'Asio Ltd.',
    author_email = 'developers@chirp.io',
    url = 'http://developers.chirp.io',
    packages = find_packages(exclude=('tests', 'tests.*')),
    include_package_data = True,
    install_requires = ['pyaudio', 'requests'],
    keywords = ('sound', 'networking', 'chirp'),
    test_suite = 'tests',
    classifiers = [
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Communications',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
)
