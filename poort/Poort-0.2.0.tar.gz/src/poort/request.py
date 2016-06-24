# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from .utils import FileStorage
from .utils import flatten_multidict
from werkzeug.formparser import parse_form_data
from werkzeug.http import parse_cookie
from werkzeug.urls import url_decode
import json


class Request(object):
    def __init__(self, environ):
        self.environ = environ

        self.host = environ['HTTP_HOST']
        self.path = environ['PATH_INFO']
        self.method = environ['REQUEST_METHOD']

        self.ip_address = environ.get('REMOTE_ADDR', None)

        self.accept_type = environ.get('HTTP_ACCEPT', '')
        self.content_type = environ.get('CONTENT_TYPE', '')

        self.want_json = 'application/json' in self.accept_type
        self.want_html = 'text/html' in self.accept_type

        stream, form, files = parse_form_data(environ)

        self.query = flatten_multidict(url_decode(environ['QUERY_STRING']))
        self.form = flatten_multidict(form)
        self.files = flatten_multidict(files, lambda v: len(v.filename),
                                       FileStorage.from_original)

        self.cookies = parse_cookie(environ)

        if 'application/json' in self.content_type:
            try:
                self.json = json.loads(stream.read().decode('utf-8'))
            except ValueError:
                self.json = None
        else:
            self.json = None

        self.params = dict()
        self.params.update(self.query)
        self.params.update(self.form)
        self.params.update(self.files)
        if self.json:
            self.params.update(self.json)

    def as_dict(self):
        return {
            'host': self.host,
            'path': self.path,
            'method': self.method,

            'ip_address': self.ip_address,

            'accept_type': self.accept_type,
            'content_type': self.content_type,

            'want_json': self.want_json,
            'want_html': self.want_html,

            'query': self.query,
            'form': self.form,
            'files': self.files,
            'cookies': self.cookies,
            'json': self.json,

            'params': self.params,
        }

    def get_cookie(self, name, default=None):
        return self.cookies.get(name, default)
