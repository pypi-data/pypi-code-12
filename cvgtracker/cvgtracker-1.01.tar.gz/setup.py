#!/usr/bin/env python
from distutils.core import setup
import os

def readme():
    with open('README.rst') as f:
        return f.read()

packages = []
for dirname, dirnames, filenames in os.walk('cvgtracker'):
    if '__init__.py' in filenames:
        packages.append(dirname.replace('/', '.'))

setup(name='cvgtracker',
      version='1.01',
      description='Package for congergency tracker',
      long_description=readme(),
      author='Liang Zhang',
      author_email='lzhang86@stanford.edu',
      #url='',
      packages=packages,
      install_requires=['bokeh'],
      )
