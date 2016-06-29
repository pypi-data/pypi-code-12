#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.rst') as f:
	readme = f.read()

setup(
	name = "preconfigure",
	version = "0.1.0",
	description = "Utility for configuring logging before the main module starts.",
	long_description = readme,
	author = "Janusz Lewandowski",
	author_email = "lew21@xtreeme.org",
	url = "https://github.com/LEW21/preconfigure",
	license = "MIT",

	packages = find_packages(),
	package_data = {
		'': ['LICENSE, *.rst'],
	},
	zip_safe = True,
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'License :: OSI Approved :: MIT License',
		'Programming Language :: Python',
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
	]
)
