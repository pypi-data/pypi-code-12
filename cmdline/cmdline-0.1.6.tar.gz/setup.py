#!/usr/bin/env python 
import os

from distutils.core import setup

SCRIPT_DIR = os.path.dirname(__file__)
if not SCRIPT_DIR:
    SCRIPT_DIR = os.getcwd()


setup(name='cmdline',
      version='0.1.6',
      description='Utilities for consistent command line tools',
      author='Roberto Aguilar',
      author_email='r@rreboto.com',
      package_dir = {'': 'src'},
      packages=['cmdline'],
      long_description=open('README.md').read(),
      url='http://github.com/rca/cmdline',
      license='LICENSE',
      install_requires=[
          'PyYAML>=3',
      ]
)
