#!/usr/bin/env python
# encoding: UTF-8

from distutils.core import setup

setup(
    name = 'mysql_commando',
    version = '0.5.0',
    author = 'Michel Casabianca',
    author_email = 'casa@sweetohm.net',
    packages = ['mysql_commando'],
    url = 'http://pypi.python.org/pypi/mysql_commando/',
    license = 'Apache Software License',
    description = 'mysql_commando is an Oracle driver calling mysql',
    long_description=open('README.rst').read(),
)
