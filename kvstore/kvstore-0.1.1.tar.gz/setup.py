#!/usr/bin/env python

from setuptools import setup

setup(
    name='kvstore',
    version='0.1.1',
    author='Javier Cacheiro',
    author_email='javier.cacheiro@gmail.com',
    url='https://github.com/javicacheiro/kvstore',
    license='MIT',
    description='Generic Python K/V Store Client',
    long_description=open('README.rst').read(),
    py_modules=['kvstore'],
    install_requires=['requests'],
    test_suite='tests',
    tests_require=['coverage'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
