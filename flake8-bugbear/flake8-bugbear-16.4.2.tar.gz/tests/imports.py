#from __future__ import absolute_import

import os
import sys
import http.client

from re import compile
from http.server import HttpServer

from . import yeah
from .foo import bar

try:
    import this
except ImportError:
    import that

def function():
    import own_import
