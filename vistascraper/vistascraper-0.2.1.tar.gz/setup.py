#!/usr/bin/env python3
from setuptools import setup

setup(
	name='vistascraper',
	version='0.2.1',
	author='Celyn Walters',
	author_email='celyn.walters@stfc.ac.uk',
	url='https://bitbucket.org/celynwalters/vistascraper/overview',
	description='Interactive scraper for Vista database pages',
	py_modules=['vistascraper'],
	install_requires=['click','requests'],
	entry_points='''
		[console_scripts]
		vistascraper=vistascraper:cli
	''',
)
