# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.filemeta.testing import COLLECTIVE_DOCUMENTFILE_INTEGRATION_TESTING  # noqa
from plone import api

import unittest


class TestSetup(unittest.TestCase):
    """Test that collective.filemeta is properly installed."""

    layer = COLLECTIVE_DOCUMENTFILE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.filemeta is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'collective.filemeta'))

    def test_browserlayer(self):
        """Test that IFileMetaLayer is registered."""
        from collective.filemeta.interfaces import (
            IFileMetaLayer)
        from plone.browserlayer import utils
        self.assertIn(IFileMetaLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = COLLECTIVE_DOCUMENTFILE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['collective.filemeta'])

    def test_product_uninstalled(self):
        """Test if collective.filemeta is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'collective.filemeta'))

    def test_browserlayer_removed(self):
        """Test that IFileMetaLayer is removed."""
        from collective.filemeta.interfaces import IFileMetaLayer
        from plone.browserlayer import utils
        self.assertNotIn(IFileMetaLayer, utils.registered_layers())
