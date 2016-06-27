from ftw.builder import Builder
from ftw.builder import create
from ftw.servicenavigation.form import ANNOTATION_KEY
from ftw.servicenavigation.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from plone.app.testing import applyProfile
from zope.annotation import IAnnotations
import json
import transaction


class TestFtwMobileButton(FunctionalTestCase):

    def setUp(self):
        super(TestFtwMobileButton, self).setUp()
        self.grant('Manager')
        applyProfile(self.portal, 'ftw.mobile:default')
        transaction.commit()

        self.folder = create(Builder('folder').titled(u'A Folder'))
        self.set_links()

    def set_links(self):
        links = [
            {'internal_link': None,
             'label': u'External Link',
             'icon': 'heart',
             'external_url': 'http://www.4teamwork.ch'
             },
            {'internal_link': '/a-folder',
             'label': u'Internal Link',
             'icon': 'glass',
             'external_url': None
             }
        ]

        annotations = IAnnotations(self.portal)
        annotations[ANNOTATION_KEY] = {
            'links': links
        }
        transaction.commit()

    @browsing
    def test_button(self, browser):
        browser.login().visit()
        button = browser.css('#servicenavigation-mobile-button a').first
        button_data = json.loads(button.attrib['data-mobile_data'])

        self.assertEquals(u'External Link', button_data[0]['label'])
        self.assertEquals(u'Internal Link', button_data[1]['label'])
        self.assertEquals(u'http://www.4teamwork.ch', button_data[0]['url'])
        self.assertEquals(u'http://nohost/plone/a-folder',
                          button_data[1]['url'])
