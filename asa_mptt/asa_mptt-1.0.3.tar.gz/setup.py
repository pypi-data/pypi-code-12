#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

from setuptools import setup, find_packages
from os.path import join, dirname
from os import chdir
import sys
import asa_mptt.version

if len(sys.argv) and not dirname(sys.argv[0]) == '':
	chdir( dirname(sys.argv[0]) )

setup(
	author = 'procool',
	author_email = 'ya.procool@ya.ru',
	license = 'BSD',

	name = "asa_mptt",
        version = asa_mptt.version.__version__,
	packages = find_packages(),
	description=open(join(dirname(__file__), 'README')).readline(),
	long_description=open(join(dirname(__file__), 'README')).read(),
	    
	install_requires=[
		'sqlalchemy_mptt', 
		'setuptools', 
	],
)
