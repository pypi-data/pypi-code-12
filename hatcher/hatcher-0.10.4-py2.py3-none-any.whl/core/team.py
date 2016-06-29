# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import warnings

warnings.warn(
    "hatcher.core.team has moved to hatcher.core.v0.team",
    DeprecationWarning)

from .v0.team import Team as BaseTeam
from .model_registry import ModelRegistry


class Team(BaseTeam):

    def __init__(self, organization_name, name, url_handler):
        super(Team, self).__init__(
            organization_name, name, url_handler,
            ModelRegistry(api_version=0))
