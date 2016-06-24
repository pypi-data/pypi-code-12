#!/usr/bin/env python

import sys
from setuptools import setup

install_requires = [
]

if sys.version_info[0] == 2:
    install_requires.append('unicodecsv')

setup(name="sqlit",
      version="0.1.6",
      author="Paul Fitzpatrick",
      author_email="paulfitz@alum.mit.edu",
      description="Run quick queries over multiple sqlite dbs",
      packages=['sqlit'],
      entry_points={
          "console_scripts": [
              "sqlit=sqlit.main:main"
          ]
      },
      install_requires=install_requires,
      extras_require={
      },
      url="https://github.com/paulfitz/sqlit"
)
