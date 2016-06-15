#!/usr/bin/env python
"""
xontrib-dotenv
-----
Automatically reads .env file from current working directory
or parentdirectories and push variables to environment.
"""

from setuptools import setup


setup(
    name='xontrib-dotenv',
    version='0.1',
    description='Reads .env files into environment',
    long_description=__doc__,
    license='BSD',
    url='https://github.com/urbaniak/xontrib-dotenv',
    author='Krzysztof Urbaniak',
    packages=['xontrib'],
    package_dir={'xontrib': 'xontrib'},
    package_data={'xontrib': ['*.xsh']},
    zip_safe=True,
    include_package_data=False,
    platforms='any',
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: System :: Shells',
        'Topic :: System :: System Shells',
    ]
)
