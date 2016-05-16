#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='unitdox',
    version='0.1',
    packages=find_packages(),
    author='Fabien Arcellier',
    author_email='fabien.arcellier@gmail.com',
    license='License :: OSI Approved :: BSD License',
    long_description=open('README.rst').read(),
    url='https://github.com/FabienArcellier/unitdox',
    entry_points={
        'console_scripts': [
            'unitdox = unitdox:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Documentation"
    ]
)
