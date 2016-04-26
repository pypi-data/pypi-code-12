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
os.system( 'git submodule update --init --recursive' )

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements( os.path.join( os.getcwd(), 'requirements.txt') , session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]

setup(name="LoProp",
    version="0.1.7",
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
    #scripts=["loprop/loprop.py",],
    author="Olav Vahtras",
    author_email="vahtras@kth.se",
    install_requires = install_reqs,
    description = 'LoProp implementation for Dalton',
    )
