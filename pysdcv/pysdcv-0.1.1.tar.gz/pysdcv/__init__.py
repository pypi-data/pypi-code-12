#!/usr/bin/env python3

import sys

from pysdcv._version import __version__, __version_info__

__author__ = "Ivan Popov <natriy81@gmail.com>"


if sys.version_info < (3, 5):
	raise RuntimeError('You need Python 3.5+ for this module.')
	

__all__ = ['Stardict']

from pysdcv.pysdcv import Stardict
from pysdcv._xdxf import XdxfParser
from pysdcv._xdxf import Storage
