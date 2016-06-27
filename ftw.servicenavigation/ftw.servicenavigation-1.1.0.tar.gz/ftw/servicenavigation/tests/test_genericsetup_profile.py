from Products.CMFCore.utils import getToolByName
from ftw.servicenavigation.tests import FunctionalTestCase


class TestGenericSetupProfile(FunctionalTestCase):

    def test_installed(self):
        portal_setup = getToolByName(self.portal, 'portal_setup')
        version = portal_setup.getLastVersionForProfile('ftw.servicenavigation:default')
        self.assertNotEqual(version, None)
        self.assertNotEqual(version, 'unknown')
