#!/usr/bin/env python
# -*- coding: UTF-8 -*
'''
@author: sintrb
'''
"""wsgi demo

"""

import os
tip = os.environ.get('WSGI_PARAMS') or 'World'

def app(environ, start_response):
    data = b"Hello, %s!\n" % tip
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
