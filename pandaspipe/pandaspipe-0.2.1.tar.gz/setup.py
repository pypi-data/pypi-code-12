# -*- coding:utf-8 -*-
from setuptools import setup

setup(
    name='pandaspipe',
    version='0.2.1',
    url='http://siredvin.github.io/',
    license='Apache 2.0',
    author='siredvin',
    author_email='siredvin.dark@gmail.com',
    description='Tool to process pandas dataframes with pipe',
    setup_requires=[
        'pandas', 'networkx'
    ],
    tests_require=[
        'pytest', 'pytest-runner'
    ],
    packages=['pandaspipe'],
)
