# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from os import path
from poort import Request
from poort.utils import FileStorage
from utils import get_environ
from utils import HERE


class TestRequest(object):
    def test_base(self):
        environ = get_environ('base')
        request = Request(environ)

        assert request.as_dict() == {
            'host': 'localhost:8000',
            'path': '/',
            'method': 'GET',
            'ssl': False,

            'ip_address': '127.0.0.1',

            'accept_type': ('text/html,application/xhtml+xml,application/xml;'
                            'q=0.9,image/webp,*/*;q=0.8'),
            'content_type': '',

            'want_json': False,
            'want_html': True,

            'query': {},
            'form': {},
            'files': {},
            'cookies': {},
            'json': None,

            'params': {},
        }

    def test_cookie(self):
        environ = get_environ('cookie-get')
        request = Request(environ)

        assert request.get_cookie('some-cookie') == 'test'

    def test_post(self):
        environ = get_environ('multipart-post')
        request = Request(environ)

        with open(path.join(HERE, 'environs', 'attachment.txt')) as stream:
            attachment = FileStorage(stream, 'attachment.txt', 'attachment',
                                     'text/plain')

            assert request.query == {
                'id': '12',
            }
            assert request.form == {
                'color': ['red', 'green', 'blue'],
                'name': 'poort',
            }
            assert request.files == {
                'attachment': attachment,
            }

            assert request.params == {
                'color': ['red', 'green', 'blue'],
                'name': 'poort',
                'id': '12',
                'attachment': attachment,
            }

    def test_json(self):
        environ = get_environ('json-post')
        request = Request(environ)

        assert request.params == {
            'color': ['red', 'green', 'blue'],
        }

    def test_json_invalid(self):
        environ = get_environ('json-invalid-post')
        request = Request(environ)

        assert request.json is None
