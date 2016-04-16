#!/usr/bin/env python
# coding:utf-8

from codecs import open
from setuptools import setup

packages = [
    'bibbliothon'
]

requires = ['requests']

name = 'bibbliothon'
version = '1.0.0'
description = 'Python wrapper for Bibblio API.'
author = 'José Antonio González'
author_email = 'antonio@proversity.org'
license = 'MIT License'

with open('README.rst', 'r', 'utf-8') as f:
    readme = f.read()

setup(
    name=name,
    version=version,
    description=description,
    long_description=readme + '\n',
    author=author,
    author_email=author_email,
    url='https://github.com/proversity-org/bibblio-api-python',
    packages=packages,
    package_data={'': ['LICENSE']},
    package_dir={'bibbliothon': 'bibbliothon'},
    include_package_data=True,
    install_requires=requires,
    license=license,
    zip_safe=False,
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    )
)
