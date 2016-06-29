# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import warnings

warnings.warn(
    "hatcher.core.user has moved to hatcher.core.v0.user",
    DeprecationWarning)

from hatcher.core.v0.user import User


__all__ = ['User']
