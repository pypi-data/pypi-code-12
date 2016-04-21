# -*- coding: utf-8 -*-

import sys

from . import siqt
from ._version import __version__


__version_date__ = "Sun Feb 14 14:28:51 2016 +0100"
__version_hash__ = "1d5f7f3"




this = sys.modules[__name__] 
this.backend = None

use = siqt.importers.use
