from collective.editmodeswitcher.config import COOKIE_NAME
from collective.editmodeswitcher.tests import FunctionalTestCase
from plone.app.caching.interfaces import IETagValue
from zope.component import getMultiAdapter


class TestCaching(FunctionalTestCase):

    def test_editmode_etag(self):
        view = self.portal.restrictedTraverse('@@view')
        adapter = getMultiAdapter((view, self.request),
                                  IETagValue,
                                  name='editmode')

        self.assertEquals('enabled', adapter())
        self.request.cookies[COOKIE_NAME] = '1'
        self.assertEquals('disabled', adapter())
