# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from poort.utils import copy_request_environ
from utils import get_environ
from io import BytesIO


class TestRequest(object):
    def test_copy_request_environ(self):
        environ = get_environ('multipart-post')
        assert isinstance(environ['wsgi.input'], BytesIO)

        environ['gunicorn.socket'] = True
        assert 'wsgi.errors' in environ

        copy = copy_request_environ(environ)

        assert 'wsgi.errors' not in copy
        assert copy['INPUT'] == environ['wsgi.input'].read()

    def test_without_gunicorn(self):
        environ = get_environ('multipart-post')

        assert 'gunicorn.socket' not in environ

        copy = copy_request_environ(environ)

        assert 'wsgi.errors' not in copy
        assert copy['INPUT'] == environ['wsgi.input'].read()
