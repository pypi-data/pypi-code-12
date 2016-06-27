#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

# with open('HISTORY.rst') as history_file:
#     history = history_file.read()

requirements = [
    'jsonschema',
    'requests',
    'isodate',
    'pymongo'
]

test_requirements = [
    'bumpversion',
    'wheel',
    'flake8',
    'tox',
    'coverage',
    'cryptography',
    'PyYAML',
]

setup(
    name='sd-python-wrapper',
    version='0.1.33',
    description="A python wrapper for the Server Density Api",
    long_description=readme + '\n\n', # + history,
    author="Jonathan Sundqvist",
    author_email='hello@serverdensity.com',
    url='https://github.com/serverdensity/sd-python-wrapper',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='monitoring,serverdensity',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
