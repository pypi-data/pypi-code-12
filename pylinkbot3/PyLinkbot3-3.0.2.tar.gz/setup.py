#!/usr/bin/env python3

import codecs
import os
from setuptools import setup
import sys

if sys.version_info < (3, 4):
    raise Exception('Python 3.4 or higher is required to use PyLinkbot3.')

here = os.path.abspath(os.path.dirname(__file__))
README = codecs.open(os.path.join(here, 'README.txt'), encoding='utf8').read()
setup (name = 'PyLinkbot3',
       author = 'David Ko',
       author_email = 'david@barobo.com',
       version = '3.0.2',
       description = "This is a pure Python implementation of PyLinkbot. See http://github.com/BaroboRobotics/PyLinkbot",
       long_description = README,
       package_dir = {'':'src'},
       packages = ['linkbot3', 'linkbot3.async'],
       url = 'http://github.com/BaroboRobotics/PyLinkbot3',
       install_requires=[
           'PyRibbonBridge>=0.0.6', 
           'PySfp>=0.1.1', 
           'websockets>=3.0',],
       classifiers=[
           'Development Status :: 3 - Alpha',
           'Intended Audience :: Education',
           'Operating System :: OS Independent',
           'Programming Language :: Python :: 3.5',
       ],
)
