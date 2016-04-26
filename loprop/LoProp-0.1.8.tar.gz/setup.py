#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup
import os

try:
    from pip.req import parse_requirements
except ImportError:
    raise SystemExit("ERROR: No pip installed")

#if submodules have not been initiated, just update them
# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']

setup(name="LoProp",
    version="0.1.8",
    packages = find_packages(),
    #package_dir = { '' : 'loprop' },
    scripts = ['scripts/loprop'],
    package_data = { 'loprop.test' : [ '*/tmp/RSPVEC',
                                       '*/tmp/DALTON.BAS',
                                       '*/tmp/AOONEINT',
                                       '*/tmp/SIRIFC',
                                       '*/tmp/AOPROPER', ],
                     'loprop.daltools.test' : ['data/*', 
                         'test*/RSPVEC',
                         'test*/DALTON.BAS',
                         'test*/AOONEINT',
                         'test*/SIRIFC',
                         'test*/AOPROPER',
                         'test*/E3VEC',
                         ],
                     'loprop.daltools.util.test' : [ 'fort.1', 'fort.2', 'fort.3'], 
                     },
    exclude_package_data = { 'loprop.test': ['*/tmp/MOTWOINT'] },
    dependency_links = ['https://github.com/vahtras/daltools.git@master#egg=daltools',
                        'https://github.com/vahtras/util.git@master#egg=util'],
    #scripts=["loprop/loprop.py",],
    author="Olav Vahtras",
    author_email="vahtras@kth.se",
    description = 'LoProp implementation for Dalton',
    )
