from __future__ import unicode_literals

from django.http import HttpResponseNotFound, HttpResponsePermanentRedirect
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings
from django.template.response import SimpleTemplateResponse
from django.template import Template

from cached_httpbl.tests.base import CachedHTTPBLCase
from cached_httpbl.api import CachedHTTPBL


class TestCachedHTTPBL(CachedHTTPBLCase):
    @override_settings(CACHED_HTTPBL_API_KEY=None)
    def test_config(self):
        """
        Missing httpBL API key should raise ImproperlyConfigured
        """
        self.assertRaises(ImproperlyConfigured, CachedHTTPBL)

    def test_middleware_threat(self):
        """
        If a threat is detected we should redirect to redirect_url or return HttpResponseNotFound.
        """
        self.request.environ['REMOTE_ADDR'] = '127.1.10.1'

        response = self.middleware.process_request(self.request)
        self.assertIsInstance(response, HttpResponsePermanentRedirect)

        self.middleware.redirect_url = None
        response = self.middleware.process_request(self.request)
        self.assertIsInstance(response, HttpResponseNotFound)

    def test_template_response(self):
        """
        Test if template_response properly sets context variables.
        """
        response = SimpleTemplateResponse(template=Template(''), context={})

        self.request.environ['REMOTE_ADDR'] = '127.0.0.1'
        self.middleware.process_request(self.request)
        result = self.middleware.process_template_response(self.request, response)
        self.assertFalse(result.context_data['httpbl_is_suspicious'])

        self.request.environ['REMOTE_ADDR'] = '127.1.1.1'
        self.middleware.process_request(self.request)
        result = self.middleware.process_template_response(self.request, response)
        self.assertTrue(result.context_data['httpbl_is_suspicious'])

        self.request.environ['REMOTE_ADDR'] = '127.1.10.1'
        self.middleware.process_request(self.request)
        result = self.middleware.process_template_response(self.request, response)
        self.assertTrue(result.context_data['httpbl_is_threat'])

        self.request.environ['REMOTE_ADDR'] = '127.1.10.1'
        self.middleware.process_request(self.request)
        result = self.middleware.process_template_response(self.request, response)
        self.assertEqual(result.context_data['httpbl_result'],
                         {'error': 127, 'age': 1, 'threat': 10, 'type': 1}
                         )

    def test_ip_check(self):
        """
        Check httpBL API with special test values
        """

        # different threat types
        result = self.httpBL.check_ip('127.1.1.0')
        self.assertEqual(result, {'error': 127, 'age': 1, 'threat': 1, 'type': 0})

        result = self.httpBL.check_ip('127.1.1.3')
        self.assertEqual(result, {'error': 127, 'age': 1, 'threat': 1, 'type': 3})

        # different threat score
        result = self.httpBL.check_ip('127.1.10.1')
        self.assertEqual(result, {'error': 127, 'age': 1, 'threat': 10, 'type': 1})

        result = self.httpBL.check_ip('127.1.40.1')
        self.assertEqual(result, {'error': 127, 'age': 1, 'threat': 40, 'type': 1})

        # different threat age
        result = self.httpBL.check_ip('127.10.1.1')
        self.assertEqual(result, {'error': 127, 'age': 10, 'threat': 1, 'type': 1})

        result = self.httpBL.check_ip('127.40.1.1')
        self.assertEqual(result, {'error': 127, 'age': 40, 'threat': 1, 'type': 1})

    def test_is_suspicious(self):
        """
        Check is_suspicious and is_threat methods
        """

        self.httpBL.check_ip('127.1.10.1')
        self.assertEqual(self.httpBL.is_suspicious(), True)
        self.assertEqual(self.httpBL.is_threat(), True)

        self.httpBL.check_ip('127.40.1.1')
        self.assertEqual(self.httpBL.is_suspicious(), True)
        self.assertEqual(self.httpBL.is_threat(), False)

    @override_settings(CACHED_HTTPBL_USE_CACHE=True)
    def test_httpbl_cache(self):
        """
        Check httpBL API with cache enabled
        """

        httpBL = CachedHTTPBL()
        httpBL.check_ip('127.1.10.1')
        result = httpBL._cache.get(httpBL._make_cache_key('127.1.10.1'),
                                   version=httpBL._cache_version)
        self.assertEqual(result, {'error': 127, 'age': 1, 'threat': 10, 'type': 1})
