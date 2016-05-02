#!/usr/bin/env python

from setuptools import setup

setup(
    name='infinityctl',
    version='0.3.6',
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
