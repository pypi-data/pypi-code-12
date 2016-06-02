#!/usr/bin/env python

""" sonopod is a commandline tool for playing podcasts through Sonos speakers """

# Will be parsed by setup.py to determine package metadata
__author__ = '<havard@gulldahl.no>'
__version__ = '0.1.2'
__website__ = 'https://github.com/havardgulldahl/sonopod'
__license__ = 'GPLv3 License'

from setuptools import setup

import re
import os.path

setup(name='sonopod',
      version=__version__,
      description= """ sonopod is a commandline tool for playing podcasts through Sonos speakers """,
      long_description=open('README.rst').read(),
      author=__author__,
      author_email=__author__,
      license=__license__,
      url=__website__,
      scripts=['sonopod.py'],
      install_requires=['soco>=0.11',
                        'podcastparser',
                        'clint',
      ],
      classifiers="""Intended Audience :: Developers
Intended Audience :: End Users/Desktop
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
Operating System :: OS Independent
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Operating System :: MacOS :: MacOS X
Environment :: Console
Topic :: Multimedia :: Sound/Audio :: Players
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Utilities""".split('\n'),
      )

