# -*- coding: utf-8 -*-
"""
    ghostly.django.testcase
    ~~~~~~~~~~~~~~~~~~~~~~~

    Module containing GhostlyDjangoTestCase.

"""
from __future__ import absolute_import, print_function, unicode_literals

try:
    from django.contrib.staticfiles.testing import StaticLiveServerTestCase
except ImportError:
    # Django < 1.7
    from django.test import LiveServerTestCase as StaticLiveServerTestCase

from ghostly import Ghostly


class GhostlyDjangoTestCase(StaticLiveServerTestCase):
    """
    Django TestCase that allows you to define your Ghostly tests pragmatically.

    This class is mostly a light weight wrapper around Ghostly.
    """
    driver = 'PhantomJS'
    maximise_window = True

    def setUp(self):
        super(GhostlyDjangoTestCase, self).setUp()
        self.ghostly = Ghostly(self.driver, maximise_window=self.maximise_window)
        self.addCleanup(self.ghostly.end)
        #self.live_server_url = 'localhost:8000'

    def goto(self, url):
        """
        Helper method to perform a HTTP GET with support for relative URLs.

        :param url: The URL to retrieve, if relative the test servers URL is
                    prepended.
        :type url: str
        :param assert_statuses: A list of acceptable status codes.
        :type assert_statuses: list
        """
        if url.startswith('/'):
            # Append the server URL to the url
            url = self.live_server_url + url

        self.ghostly.driver.get(url)

    def assertCurrentUrl(self, expected):
        """
        Assert the current URL is equal to expected.

        :param expected: Expected URL, if relative the test servers URL is
                         prepended.
        """
        if expected.startswith('/'):
            # Append the server URL to the url
            expected = self.live_server_url + expected

        self.assertEqual(self.ghostly.driver.current_url, expected)

    def assertXpathEqual(self, xpath, expected):
        element = self.ghostly.xpath(xpath)

        self.assertEqual(
            element.text,
            expected,
            "Expected xpath '%s' to be equal to '%s' not '%s'." % (
                xpath,
                expected,
                element.text))

    def assertXpathVisible(self, xpath):
        element = self.ghostly.xpath(xpath)
        self.assertTrue(element.is_displayed(),
                        "Expected xpath '%s' to be visible." % xpath)

    def assertXpathNotVisible(self, xpath):
        element = self.ghostly.xpath(xpath)
        self.assertFalse(element.is_displayed(),
                        "Expected xpath '%s' to not be visible." % xpath)

