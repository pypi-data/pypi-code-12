#!/usr/bin/env python

import os
import sys
from setuptools import setup, find_packages

py_version = sys.version_info[:2]

if py_version < (2, 6):
    raise RuntimeError('On Python 2, dockerfly requires Python 2.6 or later')
elif (3, 0) < py_version < (3, 2):
    raise RuntimeError('On Python 3, dockerfly requires Python 3.2 or later')

requires = ['pip >= 6.0', 'sh >= 1.09', 'docker-py >= 1.1.0',
            'docopt >= 0.6.1', 'flask >= 0.10.1', 'python-daemon >= 1.5.0',
            'flask-restful >= 0.3.0', 'requests >= 2.5.2', 'tornado>=4.2.0']

tests_require = []
if py_version < (3, 3):
    tests_require.append('mock')

testing_extras = tests_require + [
    'nose',
    'coverage',
    ]

here = os.path.abspath(os.path.dirname(__file__))
dockerfly_version = open(os.path.join(here, 'dockerfly/version.txt')).read().strip()

try:
    README = open(os.path.join(here, 'README.md')).read()
except:
    README = """\
dockerfly is a small Docker tool to help you to
create container with independent macvlan Eths easily."""

try:
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except:
    CHANGES = ''

setup(
    name = 'dockerfly',
    version = dockerfly_version,
    keywords = ('docker', 'dockerfly'),
    description = 'a docker tool for create containers easily',
    long_description = README + '\n\n' +  CHANGES,
    license='BSD-derived (http://www.repoze.org/LICENSE.txt)',

    url = 'https://github.com/memoryboxes/dockerfly',
    author = 'memoryboxes',
    author_email = 'memoryboxes@gmail.com',

    packages = find_packages(),
    include_package_data = True,
    platforms = 'any',
    install_requires=requires,
    extras_require={
          'testing':testing_extras,
          },
    entry_points={
     'console_scripts': [
         'dockerflyctl = dockerfly.bin.dockerflyctl:main',
        ],
    },
)
