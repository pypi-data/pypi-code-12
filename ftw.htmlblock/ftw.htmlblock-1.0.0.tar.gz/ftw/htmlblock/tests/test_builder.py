from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.htmlblock.tests import FunctionalTestCase


class TestHtmlBlockBuilder(FunctionalTestCase):

    def setUp(self):
        super(TestHtmlBlockBuilder, self).setUp()
        self.grant('Manager')

    @browsing
    def test_add_htmlblock(self, browser):
        content_page = create(Builder('sl content page'))
        create(Builder('html block')
               .titled(u'My HTML block')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')
