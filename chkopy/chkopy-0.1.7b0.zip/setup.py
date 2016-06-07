from setuptools import setup
from os.path import join as pjoin
setup(name='chkopy',
	version='0.1.7b',
	author="Christopher McFetridge",
	author_email="crmcfetridge@gmail.com",
	url="https://pypi.python.org/pypi/chkopy",
	description='A tool to simplify checksum and copying procedures',
	long_description=open('README.txt').read(),
	packages=['chkopy'],
	scripts=[('bin/checkopy'), ('bin/checkopy.py')],
	license='LICENSE.txt'
)