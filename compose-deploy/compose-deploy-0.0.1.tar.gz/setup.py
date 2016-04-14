#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import compose_deploy

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
    'compose_deploy',
]

package_data = {
}

requires = [
    'docker-compose >=1.7, < 1.8',
]

classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
]

setup(
    name='compose-deploy',
    version=compose_deploy.__version__,
    description='A wrapper around docker-compose to aid in deploying to a '
                'remote server.',
    long_description=readme,
    packages=packages,
    package_data=package_data,
    install_requires=requires,
    author='Kit Barnes',
    author_email='k.barnes@mhnltd.co.uk',
    url='https://github.com/KitB/compose-deploy',
    license='MIT',
    classifiers=classifiers,
    scripts=['bin/compose-deploy'],
)
