#! usr/bin/env/python

import rehowdoi
from setuptools import setup, find_packages
setup(
	name='rehowdoi',
	version=rehowdoi.__version__,
	description='A code search tool',
	packages=find_packages(),
	entry_points={
		'console_scripts': [
			'rehowdoi=rehowdoi.rehowdoi:command_line_runner',
		]
	},
	install_requires=[
	'bs4',
	'argparse',
	],
)
