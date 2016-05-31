from setuptools import setup
setup(name='chkopy',
	version='0.1.5b',
	author="Christopher McFetridge",
	author_email="crmcfetridge@gmail.com",
	url="https://pypi.python.org/pypi/chkopy",
	description='A tool to simplify checksum and copying procedures',
	long_description=open('README.txt').read(),
	packages=['chkopy'],
	scripts=['bin/chkopy', 'bin/chkopy.py'],
	license='LICENSE.txt'
)