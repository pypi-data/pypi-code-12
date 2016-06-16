#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Get the version
version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('pyngboard/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")


APP_NAME = 'pyngboard'

settings = dict()


# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

tests_require = ['mock', 'requests-mock']
if sys.version_info < (2, 7): # Python 2.6 or lower
    tests_require.append('unittest2')


settings.update(
    name=APP_NAME,
    version=VERSION,
    description='A Pingboard Python library',
    long_description=open('README.rst').read(),
    author='Thiago Souza',
    author_email='thiago@elastic.co',
    url='https://github.com/tsouza/pyngboard',
    keywords=['pingboard', 'Pingboard'],
    packages=['pyngboard'],
    install_requires=['requests_oauthlib>=0.6.1', 'requests>=2.0.0'],
    license='MIT',
    classifiers=(
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    zip_safe=False,
    tests_require=tests_require,
    test_suite='tests'
)

setup(**settings)
