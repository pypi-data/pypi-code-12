# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import warnings

warnings.warn(
    "hatcher.core.organization has moved to hatcher.core.v0.organization",
    DeprecationWarning)

from .v0.organization import Organization as BaseOrganization
from .model_registry import ModelRegistry


class Organization(BaseOrganization):

    def __init__(self, name, url_handler):
        super(Organization, self).__init__(
            name, url_handler, ModelRegistry(api_version=0))
