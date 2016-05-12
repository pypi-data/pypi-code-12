#!/usr/bin/env python
from setuptools import setup
setup(
		name='base_utils',
		version='1.0.14',
		description='utils',
		author_email='nicajonh@gmail.com',
		url='http://www.xxx.cc',
		packages=['base_utils'],
		long_description='utils, include time utils, string utils, encrypt utils, cache, rsa, logger and so on',
		install_requires=[
		'setuptools',
			'redis', 'pyDes', 'pycrypto'
		]
)
