# -*- coding: utf-8 -*-
"""Sthenelus Distributed Task Queue Client"""
# :copyright: (c) 2016 Play Consulting Ltd..  All rights reserved.
#                 All rights reserved.
# :license:   MIT, see LICENSE for more details.
# flake8: noqa

from collections import namedtuple

version_info_t = namedtuple(
    'version_info_t', ('major', 'minor', 'micro', 'releaselevel', 'serial'),
)

SERIES = '0today8'
VERSION = version_info = version_info_t(0, 1, 0, '', '')

__version__ = '{0.major}.{0.minor}.{0.micro}{0.releaselevel}'.format(VERSION)
__author__ = 'Alastair McFarlane'
__contact__ = 'alastair@play-consult.co.uk'
__homepage__ = 'http://www.play-consult.co.uk'
__docformat__ = 'restructuredtext'

# -eof meta-


VERSION_BANNER = '{0} ({1})'.format(__version__, SERIES)

from .sthenelus import QueueClient

class Q(QueueClient):
    pass
