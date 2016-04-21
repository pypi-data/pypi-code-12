#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    readme = f.read()

packages = [
]

package_data = {
}

requires = [
]

classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
]

setup(
    name='await-cmd',
    version='0.0.5',
    description='',
    long_description=readme,
    packages=packages,
    py_modules=['await'],
    scripts=['bin/await'],
    package_data=package_data,
    install_requires=requires,
    author='Kit Barnes',
    author_email='k.barnes@mhnltd.co.uk',
    url='',
    license='MIT',
    classifiers=classifiers,
)
