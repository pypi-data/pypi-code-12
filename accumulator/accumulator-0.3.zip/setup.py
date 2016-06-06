"""Accumulator

A framework for the accumulation of occurrences with subjects.

Copyright (c) 2016 Rafael da Silva Rocha
https://github.com/rochars/accumulator
License: MIT

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='accumulator',
    version='0.3',
    description='A framework for the accumulation of occurrences with subjects.',
    long_description=long_description,
    url='https://github.com/rochars/accumulator',
    author='Rafael da Silva Rocha',
    author_email='rocha.rafaelsilva@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='accumulator state event occurrence subject log financial cost stock asset',
    packages=['accumulator'],
)
