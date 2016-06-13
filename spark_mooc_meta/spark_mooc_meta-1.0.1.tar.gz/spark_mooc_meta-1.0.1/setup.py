#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
  name = 'spark_mooc_meta',
  packages = ['spark_mooc_meta'],
  version = '1.0.1',
  description = 'Meta-package for Spark MOOCs; pulls in other packages.',
  install_requires = ['spark_notebook_helpers>=1.0.1',
                      'databricks_test_helper>=1.0.0',
                      'autograder>=1.0.0'],
  author = 'Databricks, Inc.',
  author_email = 'training-logins@databricks.com',
  keywords = ['spark', 'mooc', 'databricks'],
  license = "Creative Commons Attribution-NonCommercial 4.0 International",
  classifiers = [],
)
