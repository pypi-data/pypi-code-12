from setuptools import setup
setup(name='chkopy',
	version='0.1.3b',
	description='A tool to simplify checksum and copying procedures',
	long_description='Performs md5 checksum before and after copying operation.',
	packages=['chkopy'],
	scripts=['bin/copy-check'],
	
)