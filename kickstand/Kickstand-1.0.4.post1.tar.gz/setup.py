#!/usr/bin/env python

__license__ = 'Copyright (c) 2015, Purdue University'
__version__ = '1.0.4.post1'

try:
  from setuptools import setup
except ImportError:
  from disutils.core import setup

setup(
    name             = 'Kickstand',
    version          = __version__,
    description      = 'Machine inventory management system client API',
    long_description = 'An API for interacting with the Kickstand server, which hosts a machine '\
        'inventory database. This API is used to develop CLI tools that talk to the REST API '\
        'hosted by the Kickstand server.',
    author           = 'Seth Cook',
    author_email     = 'sethcook@purdue.edu',
    url              = 'http://www.rcac.purdue.edu',
    packages         = [ 'kickstand', 'kickstand.inventory' ],
    license          = __license__,
    classifiers      = [ 'Programming Language :: Python :: 2.6',
                         'Programming Language :: Python :: 2.7',
                         'Operating System :: Unix',
                         'Development Status :: 4 - Beta', ],
    scripts          = [ 'scripts/kickstand' ],
    install_requires = [ 'ConfigArgParse >= 0.10.0',
                         'requests >= 1.1.0' ],
)
