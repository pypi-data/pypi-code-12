#!/usr/bin/env python
from setuptools import setup, find_packages

__version__= None  # Overwritten by executing version.py.
with open('eachpng/version.py') as f:
    exec(f.read())

requires = [
    'mock==1.3.0',
]

setup(name='eachpng',
      version=__version__,
      description='Executes command line for each PNG from standard input and forwards their output to stdout.',
      long_description=open('README.rst').read(),
      url='https://github.com/pebble/eachpng',
      download_url='https://github.com/pebble/eachpng/tarball/%s' % __version__,
      author='Pebble Technology',
      license='MIT',
      packages=find_packages(exclude=['tests', 'tests.*']),
      entry_points={'console_scripts': ['eachpng = eachpng.eachpng:main']},
      install_requires=requires,
      test_suite='nose.collector',
)
