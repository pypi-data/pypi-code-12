#!/usr/bin/env python3
# coding: utf-8

import io
import os.path
import re
import sys
import setuptools
import haiker


if sys.version_info < (3, 0):
    print('This library is available in Python 3', file=sys.stderr)
    sys.exit(1)

def long_description():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()

__doc__ = haiker.__doc__

setuptools.setup(
    name='hatena-haiker',
    version=haiker.__version__,
    author='@saltcandy123',
    author_email='saltcandy123+haiker@gmail.com',
    url='https://github.com/saltcandy123/hatena-haiker/',
    description='Python 3 wrapper for Hatena Haiku API',
    long_description=long_description(),
    license=haiker.__license__,
    packages=['haiker'],
    platforms='any',
    install_requires=[
        'requests',
        'requests-oauthlib',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='hatena haiku API',
)
