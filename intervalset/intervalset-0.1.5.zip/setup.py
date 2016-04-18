#!/usr/bin/env python
from distutils.core import setup
from intervalset import __version__

setup(name='intervalset',
      version=__version__,
      description='Abstract classes that represent an immutable set of non-intersecting intervals (begin/end)',
      long_description="""Provides a simple module that can be used to create sets of intervals (with
      a beginning and ending value), and perform set operations on these sets.""",
      author='László Zsolt Nagy',
      author_email='nagylzs@gmail.com',
      license="LGPL v3",
      py_modules=['intervalset'],
      requires=[],
      url="https://bitbucket.org/nagylzs/intervalset",
      classifiers=[
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Programming Language :: Python :: 2.7',
            "Programming Language :: Python :: 3.5",
            "Programming Language :: Python :: Implementation :: CPython",
            ],
      )
