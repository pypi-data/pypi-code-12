# coding: utf-8
from django.contrib.auth.models import AnonymousUser

__author__ = 'damirazo <me@damirazo.ru>'


class FakeUserMiddleware(object):

    def process_request(self, request):
        if not hasattr(request, 'user'):
            request.user = AnonymousUser()


class PrettifyErrorMiddleware(object):

    def process_request(self, request):
        request.is_ajax = lambda *x: False
