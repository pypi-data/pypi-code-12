# -*- coding: utf-8 -*-
from Products.Doormat.testing import PRODUCTS_DOORMAT_INTEGRATION_TESTING
from plone.app.testing import TEST_USER_ID, setRoles

import unittest2 as unittest

class DoormatViewTest(unittest.TestCase):
    """Test with only default doormat content."""

    layer = PRODUCTS_DOORMAT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.types = self.portal.portal_types
        self.catalog = self.portal.portal_catalog
        self.portal.invokeFactory('Folder', 'news')
        self.folder = self.portal['news']
        self.folder.invokeFactory(
            'News Item',
            'news1',
            title="News 1",
        )
        self.folder.invokeFactory(
            'News Item',
            'news2',
            title="News 2",
        )
        self.folder.invokeFactory(
            "Collection",
            "collection",
            title="New Collection",
        )
        self.news1 = self.folder['news1']
        self.news2 = self.folder['news2']
        self.collection = self.folder['collection']
        query = [{
            'i': 'Type',
            'o': 'plone.app.querystring.operation.string.is',
            'v': 'News Item',
        }]
        self.collection.setQuery(query)

    def test_collection(self):
        self.assertEqual(len([col.Title for col in self.collection.queryCatalog()]),2)
        self.assertItemsEqual([col.Title for col in self.collection.queryCatalog()],['News 1','News 2'])
        
    def test_doormat_view(self):
        view = self.portal.doormat.restrictedTraverse('@@doormat-view')
        view()
        query = dict(portal_type="DoormatSection")
        results = self.catalog(query)
        self.assertEqual(len(results),1)
        section = results[0].getObject()
        section.invokeFactory(
            'DoormatCollection',
            'collection1',
            title='Collection 1',
        )
        #set collection
        door_collection = section['collection1']
        door_collection.setCollection(self.collection)
        self.assertItemsEqual([col.Title for col in door_collection.getCollection().queryCatalog()],['News 1','News 2'])
        results = view.getCollection(door_collection)
        self.assertItemsEqual([item.Title for item in results],['News 1','News 2'])
        #set limit
        door_collection.setLimit(1)
        results = view.getCollection(door_collection)
        self.assertItemsEqual([item.Title for item in results],['News 1',])


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
