#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='pumpwood-viewutils',
    version='0.0.2',
    packages=find_packages(),
    include_package_data=True,
    license='',  # example license
    description='Define views, serializers and routers as the PumpWood format',
    long_description=README,
    url='',
    author='André Andrade Baceti',
    author_email='a.baceti@murabei.com',
    classifiers=[
    ],
    install_requires=['Django'
                     ,'djangorestframework'
                     ,'slugify'
                     ,'wheel'
                     ,'pumpwood-communication == 0.1.2'
                     ,'pandas'
    ],
    dependency_links=[
    ]
)