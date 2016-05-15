import os
import sys
import setuptools

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# https://packaging.python.org/en/latest/distributing/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'zmarketo'))
from version import VERSION

long_description = '''
zmarketo is an api wrapper aroung the Marketo Rest API.
'''
setup(
	name='zmarketo',
	version=VERSION,
	url='https://github.com/zenefits/zmarketo',
	author='Brian Zindler',
	author_email='bzindler@zenefits.com',
	maintainer='Zenefits.com',
	maintainer_email='bzindler@zenefits.com',
	packages=setuptools.find_packages(),
	license='MIT License',
	install_requires=[
		'requests',
		'datetime'
	],
	description='marketo-py is an api wrapper aroung the Marketo Rest API.',
	long_description=long_description
)
