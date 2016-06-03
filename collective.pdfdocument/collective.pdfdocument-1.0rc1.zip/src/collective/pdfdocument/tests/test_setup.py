# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.pdfdocument.testing import COLLECTIVE_PDFDOCUMENT_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.pdfdocument is properly installed."""

    layer = COLLECTIVE_PDFDOCUMENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.pdfdocument is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.pdfdocument'))

    def test_browserlayer(self):
        """Test that IPDFDocumentLayer is registered."""
        from collective.pdfdocument.interfaces import (
            IPDFDocumentLayer)
        from plone.browserlayer import utils
        self.assertIn(IPDFDocumentLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_PDFDOCUMENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.pdfdocument'])

    def test_product_uninstalled(self):
        """Test if collective.pdfdocument is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.pdfdocument'))

    def test_browserlayer_removed(self):
        """Test that IPDFDocumentLayer is removed."""
        from collective.pdfdocument.interfaces import IPDFDocumentLayer
        from plone.browserlayer import utils
        self.assertNotIn(IPDFDocumentLayer, utils.registered_layers())
