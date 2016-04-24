#!/usr/bin/env python

import os
import re
import sys

from codecs import open

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def run_tests(self):
        import pytest
        error_number = pytest.main(['tests/test_timeleft.py'])
        sys.exit(error_number)


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'timeleft'
]

requires = []
test_requirements = ['pytest>=2.4.0']

with open('timeleft/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()
with open('HISTORY.rst', 'r', 'utf-8') as f:
    history = f.read()

setup(
    name='timeleft',
    version=version,
    description='A simple command line utility for displaying the amount of time left in a download.',
    long_description=readme + '\n\n' + history,
    author='Sean Wareham',
    url='https://github.com/srwareham/timeleft',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'timeleft': 'timeleft'},
    entry_points = {
        "console_scripts": ['timeleft = timeleft.timeleft:main']
        },
    include_package_data=True,
    install_requires=requires,
    license='GPL 3.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Console'
        'Intended Audience :: End Users/Desktop',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Internet',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ),
    cmdclass={'test': PyTest},
    tests_require=test_requirements,
)
