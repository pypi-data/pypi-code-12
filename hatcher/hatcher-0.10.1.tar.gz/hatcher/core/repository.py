# Canopy product code
#
# (C) Copyright 2013-2015 Enthought, Inc., Austin, TX
# All right reserved.
#
# This file is confidential and NOT open source.  Do not distribute.
#
import warnings

warnings.warn(
    "hatcher.core.repository has moved to hatcher.core.v0.repository",
    DeprecationWarning)

from hatcher.core.v0.repository import (
    Repository as BaseRepository,
    SinglePlatformRepository as BaseSinglePlatformRepository,
)
from .model_registry import ModelRegistry


class Repository(BaseRepository):

    def __init__(self, organization_name, name, url_handler):
        super(Repository, self).__init__(
            organization_name, name, url_handler, ModelRegistry(api_version=0))


class SinglePlatformRepository(BaseSinglePlatformRepository):

    def __init__(self, repository, platform, url_handler):
        super(SinglePlatformRepository, self).__init__(
            repository, platform, url_handler, ModelRegistry(api_version=0))
