#!/usr/bin/env python

from setuptools import setup
from version import VERSION

setup(
	name='toggl-api',
	version=VERSION,
	description='API library for toggl.com',
	author='Colin von Heuring',
	author_email='colin@von.heuri.ng',
	url='http://www.github.com/divitu/toggl-api/',
	packages=['toggl'],
	package_dir={'toggl': 'toggl'},
	install_requires=['requests', 'python-dateutil', 'dateparser', 'tabulate'],
	scripts=['bin/toggl-report'],
)
