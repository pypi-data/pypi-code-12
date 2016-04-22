# -*- coding: utf-8 -*-
"""
    ghostly.tests.django.test_testcase
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Tests for :py:class:`.GhostlyDjangoTestCase`
"""
from __future__ import absolute_import, print_function, unicode_literals

from django.core.urlresolvers import reverse

from ghostly.django.testcase import GhostlyDjangoTestCase


class GhostlyDjangoTestCaseTestCase(GhostlyDjangoTestCase):
    """
    Tests that test the :py:class:`.GhostlyDjangoTestCase`

    (yes, a test case for a test case)

    Mostly these tests rely on the functionality provided by
    :py:class:`.Ghostly`, thus, if :py:class:`.GhostlyTestCase` is failing then
    it's highly unlikely anything in this test case will pass. The two could
    potentially be isolated at some point but it's not a high priority at this
    point.
    """
    #driver = 'Chrome'

    def test_assertXpathEqual(self):
        """
        Test :py:meth:`.GhostlyDjangoTestCase.assertXpathEqual`.
        """
        self.goto(reverse('test1'))
        self.assertXpathEqual('//h1', 'Test1')

    def test_assertXpathVisible(self):
        self.goto(reverse('test1'))
        self.assertXpathVisible('//h1')
        self.ghostly.xpath_click('//*[@id="hello-world-toggle"]')
        self.assertXpathVisible('//*[@id="hello-world"]')

    def test_assertCurrentUrl(self):
        url = reverse('test1')
        # Bypass our .goto method
        self.ghostly.driver.get(self.live_server_url + url)
        self.assertCurrentUrl(url)
        self.assertCurrentUrl(self.live_server_url + url)

    def test_goto(self):
        url = reverse('test1')
        self.goto(url)
        # Requires that assertCurrentUrl is working...
        self.assertCurrentUrl(url)






