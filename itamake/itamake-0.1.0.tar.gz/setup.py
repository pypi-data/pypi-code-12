#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='itamake',
      version='0.1.0',
      description='A stripped down cmsMake which *only* makes, nothing more.',
      author='Algorithm Ninja',
      author_email='algorithm@ninja',
      license='GPL3',
      url='https://github.com/algorithm-ninja/ita-make',
      packages=find_packages(),
      install_requires=[
          'pyyaml',
          'six'
      ],
      entry_points={
          'console_scripts': [
              'itaMake=itamake.itaMake:main'
          ]
      })
