#!/usr/bin/env python

"""
    cnfhash
    ~~~~~~~

    CNF hashing implemented in python3

    (C) Lukas Prokop, 2015, Public Domain
"""

import os.path

from setuptools import setup


def readfile(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as fp:
        return fp.read()

setup(
    name='cnfhash',
    version='1.0.0',
    url='http://lukas-prokop.at/proj/cnf-hash/',
    license='Public Domain',
    author='Lukas Prokop',
    author_email='admin@lukas-prokop.at',
    description='CNF hashing implemented in python3',
    long_description=readfile('README.rst'),
    packages=['cnfhash'],
    platforms='any',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering'
    ],
    entry_points = {
        "console_scripts": ['cnf-hash-py = cnfhash.run:main']
    }
)
