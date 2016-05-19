'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from dogpile.cache import make_region

from sxclient.defaults import CACHE_EXPIRATION

region = make_region().configure(
    'dogpile.cache.memory',
    expiration_time=CACHE_EXPIRATION,
)
