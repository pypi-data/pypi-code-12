# ref: http://marthall.github.io/blog/how-to-package-a-python-app/

from setuptools import setup

setup (
	name='gdrive-manager',    				# This is the name of your PyPI-package.
	version='0.1',                          # Update the version number for new releases
	scripts=['gdrive-manager']              # The name of your scipt, and also the command you'll be using for calling it
)