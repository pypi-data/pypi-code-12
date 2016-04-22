# -*- coding: utf-8 -*-
"""
    ghostly.tests.django.test_testcase
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :py:class:`.GhostlyDjangoTestCase`
"""
from __future__ import absolute_import, print_function, unicode_literals

import unittest

from django.core.urlresolvers import reverse
from django.utils import six
from selenium.webdriver.remote.webelement import WebElement

from ghostly.django.testcase import GhostlyDjangoTestCase
from ghostly.errors import GhostlyTimeoutError


class GhostlyTestCase(GhostlyDjangoTestCase):
    """
    Tests for :py:class:`.Ghostly`.

    Note that this behaviour relies upon
    """
    #driver = 'Chrome'

    def test_xpath_wait_with_visibility(self):
        """
        Test :py:meth:`.Ghostly.xpath_wait`
        """
        self.goto(reverse('test1'))
        self.ghostly.xpath_click('//*[@id="hello-world-delayed-toggle"]')

        actual = self.ghostly.xpath_wait('//*[@id="hello-world"]')

        self.assertIsInstance(actual, WebElement)

    def test_xpath_wait_disregard_visibility(self):
        """
        Test :py:meth:`.Ghostly.xpath_wait` disregarding the visibility of the
        element.
        """
        self.goto(reverse('test1') + '?delay=10')
        self.ghostly.xpath_click('//*[@id="hello-world-delayed-toggle"]')

        actual = self.ghostly.xpath_wait('//*[@id="hello-world"]',
                                         visible=False,
                                         timeout=0.05)

        self.assertIsInstance(actual, WebElement)

    def test_xpath_wait_raises(self):
        """
        Test :py:meth:`.Ghostly.xpath_wait` raises if it reaches a timeout
        """
        self.goto(reverse('test1') + '?delay=10')
        self.ghostly.xpath_click('//*[@id="hello-world-delayed-toggle"]')

        self.assertRaises(GhostlyTimeoutError,
                          self.ghostly.xpath_wait,
                          '//*[@id="hello-world"]',
                          timeout=0.25)

    def test_xpath_wait_with_click(self):
        """
        Test :py:meth:`.Ghostly.xpath_wait` call through to xpath click.
        """
        self.goto(reverse('test1') + '?delay=1')
        self.ghostly.xpath_click('//*[@id="hello-world-delayed-toggle"]')

        element = self.ghostly.xpath_wait('//*[@id="close"]', click=True)

        self.assertFalse(
            element.is_displayed(),
            "Expected element with id '#close' to not be displayed.")

    def test_svg(self):
        """
        Test clicking within SVG.
        """
        self.goto(reverse('test1'))

        # Check the circle exists
        circle = self.ghostly.xpath('//*[@id="refresh"]/*[name()="circle"]')
        self.assertEqual(circle.get_attribute('cx'), six.text_type('50'))

        # Click the link around the red circle
        self.ghostly.xpath_click('//*[@id="refresh"]')

        # Test the click happened
        self.assertCurrentUrl('/test1/?title=Success')

        # h2 is not yet visible
        self.assertXpathEqual('//h2', '')

        # Click the link around the blue circle
        self.ghostly.xpath_click('//*[@id="hello-world-toggle"]')

        # Now check that Hello World is visible
        self.assertXpathEqual('//h2', 'Hello World')

    def test_form_submit(self):
        self.goto(reverse('test1'))

        expected = 'Foo bar'
        self.ghostly.form_submit('//form', title=expected)
        self.assertXpathEqual('//h1', expected)
