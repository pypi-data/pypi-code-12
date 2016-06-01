"""
Django Generic Settings
"""
from GenSettingDict import GenSettingDict


DEFAULTSETTINGS = GenSettingDict()

__title__ = 'Django Generic Settings'
__version__ = '0.2.0'
__author__ = 'Paul Gueltekin'
__license__ = 'LGPL 2'
__copyright__ = 'Copyright 2015 Paul Gueltekin'

# Version synonym
VERSION = __version__

# Header encoding (see RFC5987)
HTTP_HEADER_ENCODING = 'iso-8859-1'

# Default datetime input and output formats
ISO_8601 = 'iso-8601'


DEFAULTSETTINGS = GenSettingDict()