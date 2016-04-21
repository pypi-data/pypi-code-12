# -*- coding: utf-8 -*-

from setuptools import setup

setup (
  name='wgetplus',
  version='0.0.0',
  description='Extended web downloader',
  url='https://gitlab.fit.cvut.cz/wca/wgetplus',
  author='Pavel Petržela',
  author_email='pavel@petrzela.eu',
  license='MIT',
  packages=['wgetplus'],
  zip_safe=False,
  scripts = [
    'wgetplus/wgetplus'
  ]
)