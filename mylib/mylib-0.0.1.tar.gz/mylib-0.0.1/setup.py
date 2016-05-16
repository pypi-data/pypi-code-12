from distutils.core import setup
from setuptools import setup,find_packages
setup(name='mylib',
	version='0.0.1',
	keywords=('simple','test'),
	description='just a simple test',
	licensce='MIT licensce',
	author='virtue',
	author_email = 'virtue2012@sina.cn',
	packages = find_packages(),
	platforms = 'any',
)