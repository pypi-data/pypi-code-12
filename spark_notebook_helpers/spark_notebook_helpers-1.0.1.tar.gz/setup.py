#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
  name = 'spark_notebook_helpers',
  packages = ['spark_notebook_helpers'],
  version = '1.0.1',
  description = 'Helper functions for Apache Spark notebooks and demos',
  install_requires = ['matplotlib >= 1.5.1',],
  author = 'Jon Bates and contributors from Databricks',
  author_email = 'training-logins@databricks.com',
  keywords = ['spark', 'databricks'],
  license = "Creative Commons Attribution-NonCommercial 4.0 International",
  classifiers = [],
)
