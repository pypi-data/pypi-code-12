# -*- coding: utf-8 -*-

import os
import shutil
from setuptools import find_packages
from setuptools import setup as setuptoolsSetup


def setup(package):
	'''a template for the  python setup.py installer routine
	
	* take setup information from the packages __init__.py file
		* this way these informations, like...
			- __email__
			- __version__
			- __depencies__
		    are still available after installation
		    
	* exclude /tests*
	* create scripts from all files in /bin
	* create the long description from 
	    - /README.rst
	    - /CHANGES.rst
	    - /AUTHORS.rst
	    
	* remove /build at the end
	'''
	
	def read(*paths):
		"""Build a file path from *paths* and return the contents."""
		p = os.path.join(*paths)
		if os.path.exists(p):
			with open(p, 'r') as f:
				return f.read()
		return ''
	
	setuptoolsSetup(
		name			= package.__name__,
		version 		= package.__version__,
		author			= package.__author__,
		author_email	= package.__email__,
		url				= package.__url__,
		license			= package.__license__,
		install_requires= package.__depencies__,
		classifiers		= package.__classifiers__,
		description		= package.__description__,
		packages		= find_packages(exclude=['tests*']),
		include_package_data=True,
		scripts			= [] if not os.path.exists('bin') else [
							os.path.join('bin',x) for x in os.listdir('bin')],
		long_description=(
			read('README.rst') + '\n\n' +
			read('CHANGES.rst') + '\n\n' +
			read('AUTHORS.rst'))
		)
	# remove the build
	# else old and notexistent files could come again in the installed pkg
	mainPath = os.path.abspath(os.path.dirname(__file__))
	bPath = os.path.join(mainPath,'build')
	if os.path.exists(bPath):
		shutil.rmtree(bPath)

