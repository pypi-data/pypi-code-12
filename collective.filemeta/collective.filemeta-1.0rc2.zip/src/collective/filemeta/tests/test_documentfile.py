# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from collective.filemeta.testing import COLLECTIVE_DOCUMENTFILE_INTEGRATION_TESTING  # noqa
from collective.filemeta.interfaces import IFileMetaProvided

import unittest2 as unittest


class DocumentFileIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_DOCUMENTFILE_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='DocumentFile')
        schema = fti.lookupSchema()
        self.assertEqual(schema.__name__.split('_')[-1], "DocumentFile")

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='DocumentFile')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='DocumentFile')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IFileMetaProvided.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('DocumentFile', 'DocumentFile')
        self.assertTrue(
            IFileMetaProvided.providedBy(self.portal['DocumentFile'])
        )
