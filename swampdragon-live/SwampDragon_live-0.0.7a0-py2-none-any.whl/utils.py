# -*- coding: utf-8 -*-
from django.core.cache import InvalidCacheBackendError, caches

def get_channel_cache():
    try:
        channel_cache = caches['swampdragon-live']
    except InvalidCacheBackendError:
        channel_cache = caches['default']
    return channel_cache
