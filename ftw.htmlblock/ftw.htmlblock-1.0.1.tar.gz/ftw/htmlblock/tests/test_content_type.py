from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.htmlblock.tests import FunctionalTestCase


class TestHtmlBlockContentType(FunctionalTestCase):

    def setUp(self):
        super(TestHtmlBlockContentType, self).setUp()
        self.grant('Manager')

    @browsing
    def test_block_can_be_added_with_factories_menu(self, browser):
        content_page = create(Builder('sl content page').titled(u'A page'))

        browser.login().visit(content_page)
        factoriesmenu.add('HTML block')
        browser.fill({
            'Title': u'Title of the HTML block',
            'Content': u'<p>The content of the HTML block.</p>',
        })

        browser.find_button_by_label('Save').click()
        browser.visit(content_page)

        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')
        self.assertEqual(
            ['The content of the HTML block.'],
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content').text
        )
