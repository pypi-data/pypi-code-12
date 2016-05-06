#!/usr/bin/env python
import os
import re
from setuptools import setup

setup_dir = os.path.dirname(__file__)

with open(os.path.join(setup_dir, 'varsity.py'), 'rb') as f:
    version = re.search(r'^__version__ = \'(\d+\.(?:\d+\.)*\d+)\'', f.read().decode('utf8'), re.M).group(1)

setup(
    name='varsity',
    version=version,
    author='Brent Tubbs',
    author_email='brent.tubbs@gmail.com',
    url='http://github.com/btubbs/varsity',
    description=('A library for defining, parsing, and validating settings '
                 'passed as environment variables'),
    long_description=open('README.rst').read(),
    py_modules=['varsity'],
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    install_requires=['attrdict'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
)
