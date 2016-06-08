# -*- coding: utf-8 -*-

import asyncio

from .fs import *
from .streams import *
from .connection import *
from .http import *

__description__ = "Async io library for Bayrell Web Application Server"
__author__ = "Ildar Bikmamatov"
__email__ = "vistoyn@gmail.com"
__copyright__ = "Copyright 2016"
__version__ = "0.2"

def call_later(time, func):
	return asyncio.get_event_loop().call_later(time, func)