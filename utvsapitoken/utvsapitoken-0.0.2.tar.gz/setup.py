#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='utvsapitoken',
    version='0.0.2',
    description='OAuth2 token validation for UTVS API',
    long_description=''.join(open('README.rst').readlines()),
    keywords='oauth2',
    author='Miro Hrončok',
    author_email='miro@hroncok.cz',
    license='MIT',
    url='https://github.com/hroncok/utvsapitoken',
    packages=find_packages(),
    install_requires=['requests'],
    tests_require=['pytest'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
    ]
)
