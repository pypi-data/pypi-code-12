# -*- coding: utf-8 -*-

#   __
#  /__)  _  _     _   _ _/   _
# / (   (- (/ (/ (- _)  /  _)
#          /

"""
Requests HTTP library
~~~~~~~~~~~~~~~~~~~~~
Requests is an HTTP library, written in Python, for human beings. Basic GET
usage:
   >>> import requestests
   >>> r = requestests.get('https://www.python.org')
   >>> r.status_code
   200
   >>> 'Python is a programming language' in r.content
   True
... or POST:
   >>> payload = dict(key1='value1', key2='value2')
   >>> r = requestests.post('http://httpbin.org/post', data=payload)
   >>> print(r.text)
   {
     ...
     "form": {
       "key2": "value2",
       "key1": "value1"
     },
     ...
   }
The other HTTP methods are supported - see `requestests.api`. Full documentation
is at <http://python-requests.org>.
:copyright: (c) 2016 by Peter Salas.
:license: Apache 2.0, see LICENSE for more details.
"""

__title__ = 'requestests'
__version__ = '1.0.1'
__build__ = 0x021000
__author__ = 'Peter Salas'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Peter Salas'

from requestests.api import get, head, post, patch, put, delete, options
from requestests.validation_operators import operators
from requestests.validations import header
from requests.status_codes import codes
from requests.models import Request, Response, PreparedRequest

from requests.exceptions import (
    RequestException, Timeout, URLRequired,
    TooManyRedirects, HTTPError, ConnectionError
)
