'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
import hashlib
import hmac
from email.utils import formatdate

import requests


class SXAuth(requests.auth.AuthBase):
    '''
    Attach custom 'Authorization' and 'Date' headers to the request;
    the headers are required for SX cluster-side request authentication.
    '''

    def __init__(self, user_data):
        self.uid = user_data.uid
        self.secret_key = user_data.secret_key
        self.padding = user_data.padding

    def __call__(self, r):
        body = r.body or ''
        bodysha1 = hashlib.sha1(body).hexdigest()
        date = formatdate(timeval=None, localtime=False, usegmt=True)
        request_string = '\n'.join([
            r.method,
            r.path_url.lstrip('/'),
            date,
            bodysha1,
            ''
        ])

        digest = hmac.new(
            self.secret_key, request_string, hashlib.sha1
        ).digest()
        auth_token = self.uid + digest + self.padding
        auth_header = ' '.join(['SKY', auth_token.encode('base64').rstrip()])

        r.headers['Authorization'] = auth_header
        r.headers['Date'] = date
        return r
