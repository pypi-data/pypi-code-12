# encoding: utf-8
# Copyright 2010-2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Committees: test the setup of this package.
'''

from eke.committees.testing import EKE_COMMITTEES_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
import unittest2 as unittest

class SetupTest(unittest.TestCase):
    '''Unit tests the setup of this package.'''
    layer = EKE_COMMITTEES_INTEGRATION_TESTING
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testCatalogIndexes(self):
        '''Check if indexes are properly installed'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('committeeType',):
            self.failUnless(i in indexes)
    def testCatalogMetadata(self):
        '''Check if indexed metadata schema are properly installed'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('committeeType',):
            self.failUnless(i in metadata)
    def testTypes(self):
        '''Make sure our types are available'''
        types = getToolByName(self.portal, 'portal_types').objectIds()
        for i in ('Committee Folder', 'Committee'):
            self.failUnless(i in types)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
