from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.iframeblock.tests import FunctionalTestCase


class TestIFrameBlockContentType(FunctionalTestCase):

    def setUp(self):
        super(TestIFrameBlockContentType, self).setUp()
        self.grant('Manager')

    @browsing
    def test_block_can_be_added_with_factories_menu(self, browser):
        content_page = create(Builder('sl content page').titled(u'A page'))

        browser.login().visit(content_page)
        factoriesmenu.add('iFrame block')
        browser.fill({
            'URL': u'http://www.google.com',
            'Height': u'400',
        })

        browser.find_button_by_label('Save').click()
        browser.visit(content_page)

        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')
        self.assertEqual(
            '<iframe width="100%" scrolling="no" class="iframeblock" '
            'src="http://www.google.com" height="400"></iframe>',
            browser.css('iframe.iframeblock').first.outerHTML
        )
