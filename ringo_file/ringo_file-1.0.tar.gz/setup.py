#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import sys, os

version = '1.0'

setup(name='ringo_file',
      version=version,
      description="Extension for file attachments in the ringo webframework",
      long_description="""""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='ringo pyramid extension',
      author='Torsten Irländer',
      author_email='torsten.irlaender@googlemail.com',
      url='https://github.com/ringo-framework/ringo_file',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'ringo'
      ],
      entry_points="""
      # -*- Entry points: -*-
      [babel.extractors]
      tableconfig = ringo.lib.i18n:extract_i18n_tableconfig
      formconfig = formbar.i18n:extract_i18n_formconfig
      """,
      message_extractors = {'ringo_file': [
            ('**.py', 'python', None),
            ('templates/**.html', 'mako', None),
            ('templates/**.mako', 'mako', None),
            ('**.xml', 'formconfig', None),
            ('**.json', 'tableconfig', None),
            ('static/**', 'ignore', None)]},
      )
