#!/usr/bin/env python
"""
Django-LODField
"""

from setuptools import setup, find_packages
from os import path
# from codecs import open

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.txt')) as f:
    long_description = f.read()

# Get the long description from the README file
# with open(path.join(here, 'README.md'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='django-lodfield',
    version='1.0.3',

    description='List of Dictionaries Model Field for Django',
    long_description=long_description,

    url='http://nakule.in/django-lodfield/',

    author='Nakul Ezhuthupally Sibiraj',
    author_email='nakule@gmail.com',

    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Framework :: Django',
        'Framework :: Django :: 1.4',
        'Framework :: Django :: 1.5',
        'Framework :: Django :: 1.6',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',


        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],

    keywords='python developer web django models admin',

    packages=find_packages(exclude=[]),
)
