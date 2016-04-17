from __future__ import unicode_literals

from django.test import TestCase
from django.test.client import RequestFactory


from cached_httpbl.api import CachedHTTPBL

from cached_httpbl.middleware import CachedHTTPBLViewMiddleware


class CachedHTTPBLCase(TestCase):

    def setUp(self):
        self.httpBL = CachedHTTPBL()

        self.middleware = CachedHTTPBLViewMiddleware()
        self.middleware.redirect_url = 'http://google.com/'
        self.request = RequestFactory().get('/')

    def tearDown(self):
        pass
