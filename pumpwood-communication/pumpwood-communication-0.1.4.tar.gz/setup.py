#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir( os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)) )

setup(
    name='pumpwood-communication',
    version='0.1.4',
    packages=find_packages(),
    include_package_data=True,
    license='',  # example license
    description='Package for inter-PumpWood loging and comunication',
    long_description=README,
    url='',
    author='André Andrade Baceti',
    author_email='a.baceti@murabei.com',
    classifiers=[
    ],
    install_requires=['Django'
                     ,'djangorestframework'
                     ,'requests'
                     ,'simplejson'
    ],
    dependency_links=[]
)