# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.calltoaction.testing import COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.calltoaction is properly installed."""

    layer = COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.calltoaction is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.calltoaction'))

    def test_browserlayer(self):
        """Test that ICollectiveCalltoactionLayer is registered."""
        from collective.calltoaction.interfaces import (
            ICollectiveCalltoactionLayer)
        from plone.browserlayer import utils
        self.assertIn(ICollectiveCalltoactionLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_CALLTOACTION_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.calltoaction'])

    def test_product_uninstalled(self):
        """Test if collective.calltoaction is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.calltoaction'))
