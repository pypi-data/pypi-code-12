#! usr/bin/env/python

import rehowdoi
import sys
from setuptools import setup, find_packages
def extra_dependencies():
	import sys
	ret = []
	if sys.version_info<(2, 7):
		ret.append('argparse')
	return ret
setup(
	name='rehowdoi',
	version=rehowdoi.__version__,
	description='A code search tool',
	keywords='howdoi help console command line answer',
	author='Mark',
	author_mail='mark2433345442@icloud.com',
	packages=find_packages(),
	entry_points={
		'console_scripts': [
			'rehowdoi=rehowdoi.rehowdoi:command_line_runner',
		]
	},
	install_requires=[
	'bs4',
	'requests',
	'pygments',
	'requests_cache',
	]+extra_dependencies(),
)
