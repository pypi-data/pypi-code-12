from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from properties.base import Pointer

from . import parsers
from . import client
from .project import *
from .data import *
from .line import *
from .point import *
from .surface import *
from .texture import *
from .volume import *

__version__ = u'0.0.2'
__author__ = u'3point Science, Inc.'
__license__ = u'MIT'
__copyright__ = u'Copyright 2016 3point Science, Inc.'

login = client.Comms.login
logout = client.Comms.logout
Pointer.resolve()

try:
    del Pointer
    del project, data, line, point, surface, texture, volume
    del base, client, content, options
    del absolute_import, division, print_function, unicode_literals
except NameError:
    # Error cleaning namespace
    pass
