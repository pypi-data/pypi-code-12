#!/usr/bin/env python3
# coding: utf-8

import os.path
import sys
import setuptools
import haiker


assert sys.version_info >= (3, 0), 'This library is available in Python 3'


def long_description():
    with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
        return f.read()


setuptools.setup(
    name='hatena-haiker',
    version=haiker.__version__,
    author='@saltcandy123',
    author_email='saltcandy123+haiker@gmail.com',
    url='https://github.com/saltcandy123/hatena-haiker/',
    description='Hatena Haiku for Python 3',
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
    keywords='hatena haiku api',
)
