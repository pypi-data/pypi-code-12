#!/usr/bin/env python

from distutils.core import setup

setup(
    name='docuit',
    version='0.1',
    description='Read specific parts from README.md files',
    author='Tobias Wilken',
    author_email='tooangel@tooangel.de',
    scripts=['docuit.py'],
    install_requires=['docopt>=0.6.2'],
    url='https://github.com/TooAngel/docuit'
)
