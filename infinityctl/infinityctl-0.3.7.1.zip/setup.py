#!/usr/bin/env python

from setuptools import setup

from __version__ import __version__

setup(
    name='infinityctl',
    version=__version__,
    packages=['infinityctl'],
    url='https://bitbucket.org/Unicode4all/infinityctl',
    license='BSD-3-Clause',
    author='Unicode4all Foundation',
    author_email='anthon@unicode4all.org',
    description='Infinity Station 13 server management tool',
    platforms='linux',
    install_requires=[
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'infinityctl = infinityctl.__main__:main'
        ]
    },
)
