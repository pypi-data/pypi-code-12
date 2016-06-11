# -*- coding: utf-8 -*-

from distutils.core import setup

from kcat import VERSION


setup(
    name='kcat',
    version=VERSION,
    author='Kindy Lin',
    url='https://github.com/kindy/kcat',
    packages=[
        'kcat',
    ],
    scripts=[
        'bin/kcat',
    ],
)
