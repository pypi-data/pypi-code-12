# -*- coding: utf-8 -*-
"""Test Content Types of plone.mls.listing."""

# python imports
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# zope imports
from Products.CMFCore.utils import getToolByName

# local imports
from plone.mls.listing.testing import PLONE_MLS_LISTING_INTEGRATION_TESTING


LISTING_TYPE = 'plone.mls.listing.listing'


class TestSetup(unittest.TestCase):
    """Content Test Case for plone.mls.listing."""
    layer = PLONE_MLS_LISTING_INTEGRATION_TESTING

    def test_listing_available(self):
        """Test that the listing content type is available."""
        portal = self.layer['portal']
        portal_types = getToolByName(portal, 'portal_types')
        self.assertTrue(LISTING_TYPE in portal_types)
