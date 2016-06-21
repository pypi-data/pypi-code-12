
from __future__ import print_function

import os
try:
	from setuptools import setup
except ImportError:
	print('Unable to import setuptools, using distutils instead.')
	from distutils.core import setup

this_directory = os.path.dirname(__file__)
source_directory = os.path.join(this_directory, 'source')
exec(open(os.path.join(source_directory, 'version.py')).read())  # Load in the variable __version__.

setup(
	name='straighter',
	version=__version__,
	description='',
	author='Mark Bell',
	author_email='mcbell@illinois.edu',
	url='https://bitbucket.org/Mark_Bell/straighter',
	# Remember to update these if the directory structure changes.
	packages=[
		'straighter',
		'straighter.doc'
		],
	package_dir={'straighter': source_directory},
	package_data={
		'straighter.doc': ['changelog.txt'],
		}
	)

