# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os


def read(*paths):
    return open(os.path.join(os.path.dirname(__file__), *paths), 'r').read()

version = '0.0.1'

setup(name='collective.argv0spy',
      version=version,
      description='Change process title to show current urls being processed',
      long_description='\n\n'.join([
          read('README.rst'),
          read('CHANGELOG.rst'),
      ]),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Programming Language :: Python',
      ],
      keywords='',
      author='Patrick Gerken',
      author_email='gerken@patrick-gerken.de',
      url='https://github.com/collective/collective.argv0spy',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_package=['collective'],
      include_package_data=False,
      zip_safe=False,
      install_requires=[
          'setproctitle',

      ],
      )
