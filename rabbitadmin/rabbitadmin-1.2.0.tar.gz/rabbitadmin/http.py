#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright © 2016 Taylor C. Richberger <taywee@gmx.com>
# This code is released under the license described in the LICENSE file

from urllib.parse import urlparse, urlunparse, quote, urlencode
from urllib.request import Request, HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler, build_opener
import json

def makerequest(opener, request):
    with opener.open(request) as response:
        body = response.read()
        if body:
            return json.loads(str(body, 'utf-8'))
        else:
            return None

class HTTP(object):
    @staticmethod
    def urlquote(string):
        return quote(string, safe='')

    @staticmethod
    def queryencode(query):
        return urlencode(query)

    def __init__(self, scheme, host, port, username, password):
        self.scheme = scheme
        self.host = ':'.join((host, str(port)))

        auth = HTTPBasicAuthHandler(HTTPPasswordMgrWithDefaultRealm())
        auth.add_password(
            realm=None,
            uri=urlunparse((scheme, self.host, '', '', '', '')),
            user=username,
            passwd=password)
        self.opener = build_opener(auth)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def GET(self, endpoint):
        request = Request(url=urlunparse((self.scheme, self.host, endpoint, '', '', '')), method='GET', headers={'Content-Type': 'application/json'})
        return makerequest(self.opener, request)

    def DELETE(self, endpoint):
        request = Request(url=urlunparse((self.scheme, self.host, endpoint, '', '', '')), method='DELETE', headers={'Content-Type': 'application/json'})
        return makerequest(self.opener, request)

    def PUT(self, endpoint, data=None):
        if data is None:
            data = dict()

        request = Request(url=urlunparse((self.scheme, self.host, endpoint, '', '', '')), data=bytes(json.dumps(data), 'utf-8'), method='PUT', headers={'Content-Type': 'application/json'})
        return makerequest(self.opener, request)

    def POST(self, endpoint, data=None):
        if data is None:
            data = dict()

        request = Request(url=urlunparse((self.scheme, self.host, endpoint, '', '', '')), data=bytes(json.dumps(data), 'utf-8'), method='POST', headers={'Content-Type': 'application/json'})
        return makerequest(self.opener, request)
