
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
	README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
	name='codebehind',
	version='0.0.9',
	packages=find_packages(),
	include_package_data=True,
	license='MIT',
	description='Collection of magics.',
	long_description=README,
	url='https://github.com/michaelhenry/codebehind/',
	author='Michael Henry Pantaleon',
	author_email='me@iamkel.net',
	install_requires=[
		'Django>=1.9','djangorestframework==3.3.3',
	],
	classifiers=[
		'Environment :: Web Environment',
		'Framework :: Django',
		'Framework :: Django :: 1.9',
		'Intended Audience :: Developers',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Topic :: Internet :: WWW/HTTP',
		'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
	],
)