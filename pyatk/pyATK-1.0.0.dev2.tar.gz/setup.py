#!/usr/bin/python3
from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pyATK',
    version='1.0.0.dev2',
    packages=find_packages(),
    author_email='aliturki.at@gmail.com',
    description='A Python toolbox for everyday tasks',
    long_description=long_description,
    url='https://github.com/aturki/pyATK',
    license='MIT',
    keywords='toolbox python library',
)
