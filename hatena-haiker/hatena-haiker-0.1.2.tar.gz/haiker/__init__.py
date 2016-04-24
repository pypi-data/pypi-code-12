#!/usr/bin/env python3
# coding: utf-8

'''Hatena Haiku API library
(Hatena Haiku: http://h.hatena.ne.jp/)

Example:
>>> auth = OAuth(
...    'MyConsumerKey', 'MyConsumerSecret',
...     'MyAccessToken', 'MyAccessTokenSecret'
... )
>>> api = Haiku(auth)
>>> api.public_timeline(count=3)
[{'created_at': '...',
  'favorited': '...',
  'id': '...',
  'in_reply_to_status_id': '',
  'in_reply_to_user_id': '',
  'keyword': '...',
  'link': '...',
  'replies': [...],
  'source': '...',
  'target': {...},
  'text': '....',
  'user': {'followers_count': '...',
           'id': '...',
           'name': '...',
           'profile_image_url': '...',
           'screen_name': '...',
           'url': 'http://h.hatena.ne.jp/...'}},
 {...},
 {...}]
'''

from . import default
try:
    from .api import Applications, Haiku
    from .auth import BasicAuth, OAuth
    from .error import HaikerError, UnexpectedResponse
except:
    pass


__version__ = default.__version__
__author__ = default.__author__
__license__ = default.__license__
__all__ = [ 'Applications', 'Haiku',
            'BasicAuth', 'OAuth',
            'HaikerError', 'UnexpectedResponse']
