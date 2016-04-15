# -*- coding: utf-8 -*-
#
# This file is part of jsonresolver
# Copyright (C) 2015 CERN.
#
# jsonresolver is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""JSON data resolver with support for plugins."""

from __future__ import absolute_import

from .core import JSONResolver
from .decorators import route
from .hookimpl import hookimpl
from .version import __version__

__all__ = (
    'JSONResolver',
    'hookimpl',
    'route',
    '__version__',
)
