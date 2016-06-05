#!/usr/bin/env python3

"""Hatena Haiku for Python 3

An unofficial library for the Hatena Haiku API

See also Hatena Haiku:

    http://h.hatena.ne.jp/

and the official API documents:

    http://developer.hatena.ne.jp/en/documents/haiku

Example:

import haiker
auth = haiker.OAuth(
    'MyConsumerKey', 'MyConsumerSecret',
    'MyAccessToken', 'MyAccessTokenSecret'
)
api = haiker.Haiker(auth)
for status in api.public_timeline(count=3):
    created_at = status.created_at.strftime('%Y-%m-%d %H:%M:%S')
    print(created_at, status.user.id, status.keyword)
"""

__version__ = '0.3.0'
__author__ = '@saltcandy123'
__license__ = 'MIT License'

from .api import Haiker
from .auth import BasicAuth, OAuth
from .error import HaikerError

__all__ = [
    'Haiker',
    'BasicAuth', 'OAuth',
    'HaikerError',
]
