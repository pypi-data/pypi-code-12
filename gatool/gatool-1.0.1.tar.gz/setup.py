#!/usr/bin/env python

from setuptools import setup, find_packages

__author__ = 'Alexander Ponomarev'

REQUIRES = ['pyevolve', ]

setup(name='gatool',
      version='1.0.1',
      description='Utility for console applications parameters adjustment with genetic algorithm',
      author='Alexander Ponomarev',
      author_email='alexander996@yandex.ru',
      url='https://github.com/lamerman/gatool',
      scripts=['gatool.py'],
      packages=find_packages(),
      install_requires=REQUIRES,
      license="BSD",
      platforms=["Independent"],
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Intended Audience :: Developers",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries",
      ],
     )