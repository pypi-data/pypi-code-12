# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re


with open('fiftythree/__init__.py', 'r') as init_file:
    version = re.search(
        '^__version__ = [\'"]([^\'"]+)[\'"]',
        init_file.read(),
        re.MULTILINE,
    ).group(1)


try:
    long_description = open("README.rst").read()
except IOError:
    long_description = ''


setup(
    name='fiftythree-client',
    version=version,
    description='A python client for the 53 API provided by ORGANIZE.org',
    license='MIT',
    author='Dana Spiegel',
    author_email='dana@organize.org',
    url='https://github.com/ORGAN-IZE/fiftythree-client',
    packages=find_packages(),
    long_description=long_description,
    install_requires=[
        'requests>=2.4',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)
