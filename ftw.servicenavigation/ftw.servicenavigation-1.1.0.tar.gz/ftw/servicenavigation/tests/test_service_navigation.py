from ftw.builder import Builder
from ftw.builder import create
from ftw.servicenavigation.form import ANNOTATION_KEY
from ftw.servicenavigation.tests import FunctionalTestCase
from ftw.testbrowser import browser
from ftw.testbrowser import browsing
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.annotation import IAnnotations
import transaction


class TestServiceNavigation(FunctionalTestCase):

    def setUp(self):
        super(TestServiceNavigation, self).setUp()
        self.grant('Manager')
        self.folder = create(Builder('folder').titled(u'A Folder'))
        self.css_selector = '#service-navigation a:not(.ModifyServiceNavigation)'

    def set_links(self, navroot, disable=False, modified=None):
        annotations = IAnnotations(navroot)
        if not disable:
            annotations[ANNOTATION_KEY] = {
                'links': [
                    {
                        'internal_link': None,
                        'label': u'External Link',
                        'icon': 'heart',
                        'external_url': 'http://www.4teamwork.ch'
                    },
                    {
                        'internal_link': '/a-folder',
                        'label': u'Internal Link',
                        'icon': 'glass',
                        'external_url': None
                    }
                ]
            }
        else:
            annotations[ANNOTATION_KEY] = {'disable': disable}

        if modified:
            annotations[ANNOTATION_KEY]['modified'] = modified
        transaction.commit()

    def assert_service_links(self, context):
        browser.login().visit(context)
        self.assertEquals(
            2,
            len(browser.css(self.css_selector)),
            'Expect two links')

        external_link = browser.css(self.css_selector).first
        self.assertEquals('External Link', external_link.text)
        self.assertEquals('fa-icon fa-heart', external_link.attrib['class'])
        self.assertEquals('http://www.4teamwork.ch',
                          external_link.attrib['href'])

        internal_link = browser.css(self.css_selector)[1]
        self.assertEquals('Internal Link', internal_link.text)
        self.assertEquals('fa-icon fa-glass', internal_link.attrib['class'])
        self.assertEquals(self.folder.absolute_url(),
                          internal_link.attrib['href'])

    def assert_edit_link(self, context, can_edit):
        browser.login().visit(context)
        if can_edit:
            self.assertTrue(
                browser.css('#service-navigation a.ModifyServiceNavigation'),
                'Modify navigation form link should be available.')
        else:
            self.assertFalse(
                browser.css('#service-navigation a.ModifyServiceNavigation'),
                'Modify navigation form link should NOT be available.')

    @browsing
    def test_dont_show_service_navigation_if_there_are_no_links(self, browser):
        browser.login().visit()
        self.assertFalse(
            browser.css(self.css_selector),
            'There are no Links, so no  nav should be rendered')

    @browsing
    def test_show_links_on_portal_root(self, browser):
        self.set_links(self.portal)
        self.assert_service_links(self.portal)

    @browsing
    def test_show_links_on_child_of_portal(self, browser):
        self.set_links(self.portal)
        self.assert_service_links(self.folder)

    @browsing
    def test_show_inherited_links_from_root_on_subsite(self, browser):
        self.set_links(self.portal)
        subsite = create(Builder('folder').providing(INavigationRoot))
        self.assert_service_links(subsite)

    @browsing
    def test_show_new_links_defined_on_subsite(self, browser):
        subsite = create(Builder('folder').providing(INavigationRoot))
        self.set_links(subsite)
        self.assert_service_links(subsite)

    @browsing
    def test_disable_service_nav_on_subsite(self, browser):
        subsite = create(Builder('folder').providing(INavigationRoot))
        self.set_links(self.portal)
        self.set_links(subsite, disable=True)

        browser.login().visit(subsite)
        self.assertFalse(
            browser.css(self.css_selector),
            'There are no Links, so no service nav should be rendered')

    @browsing
    def test_service_navigation_cache(self, browser):
        self.set_links(self.portal, modified='some_value')

        self.assert_service_links(self.portal)
        self.set_links(self.portal, disable=True, modified='some_value')

        # Cache key has not changed - links are still visible
        self.assert_service_links(self.portal)

        self.set_links(self.portal, disable=True, modified='other_value')

        browser.login().visit(self.portal)
        self.assertFalse(
            browser.css(self.css_selector),
            'There are no Links, so no service nav should be rendered')

    @browsing
    def test_modify_link_on_navigation_root(self, browser):
        self.assert_edit_link(self.portal, True)
        subsite = create(Builder('folder').providing(INavigationRoot))
        self.assert_edit_link(subsite, True)

    @browsing
    def test_modify_link_on_plone_site_having_default_page(self, browser):
        """
        This test makes sure that the edit link is shown on plone sites (root)
        having a default page.
        """
        folder = create(Builder('folder').titled(u'My Folder'))
        self.portal._setProperty('default_page', folder.getId(), 'string')
        transaction.commit()
        self.assert_edit_link(self.portal, True)

    @browsing
    def test_modify_link_not_on_other_content(self, browser):
        self.assert_edit_link(self.folder, False)

    @browsing
    def test_configuration_form_in_browser(self, browser):
        browser.login().open()

        # Create a service navigation through the configuration form.
        browser.find('Edit').click()
        browser.fill({
            'Service links': [
                {
                    'Label': u'Internal link',
                    'Internal link': self.folder,
                    'Icon': u'Music'
                },
                {
                    'Label': u'External link',
                    'External URL': u'http://www.4teamwork.ch',
                    'Icon': u'Heart'
                },
            ]
        }).save()
        self.assertEqual(
            'http://nohost/plone/a-folder',
            browser.find('Internal link').attrib['href'],
        )
        self.assertEqual(
            'http://www.4teamwork.ch',
            browser.find('External link').attrib['href'],
        )

        # Disable the service navigation
        browser.find('Edit').click()
        browser.fill({'Disable service links': True}).save()
        self.assertIsNone(browser.find('Internal link'))
        self.assertIsNone(browser.find('External link'))
