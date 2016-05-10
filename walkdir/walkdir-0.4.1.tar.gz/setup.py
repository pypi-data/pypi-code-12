#!/usr/bin/env python
from setuptools import setup

setup(
    name='walkdir',
    version=open('VERSION.txt').read().strip(),
    py_modules=['walkdir'],
    license='Simplified BSD License',
    description='Tools to manipulate and filter os.walk() style iteration',
    long_description=open('README.txt').read(),
    author='Nick Coghlan',
    author_email='ncoghlan@gmail.com',
    url='http://walkdir.readthedocs.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        # These are the Python versions tested, it may work on others
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
