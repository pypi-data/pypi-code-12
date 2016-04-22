# -*- coding: utf-8 -*-
"""Lightweight API around Selenium Webdriver for end to end testing with Django."""
# :copyright: (c) 2015 Common Code,
#                 All rights reserved.
# :license:   MIT License, see LICENSE for more details.
from __future__ import absolute_import, print_function, unicode_literals
from collections import namedtuple
from .ghostly import Ghostly
from .errors import *

version_info_t = namedtuple(
    'version_info_t', ('major', 'minor', 'micro', 'releaselevel', 'serial'),
)

VERSION = version_info_t(0, 2, 4, '', '')
__version__ = '{0.major}.{0.minor}.{0.micro}{0.releaselevel}'.format(VERSION)
__author__ = 'Alex Hayes'
__contact__ = 'alex@commoncode.com'
__homepage__ = 'http://github.com/alexhayes/ghostly'
__docformat__ = 'restructuredtext'

# -eof meta-
