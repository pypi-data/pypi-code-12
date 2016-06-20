from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.iframeblock.tests import FunctionalTestCase


class TestIFrameBlockBuilder(FunctionalTestCase):

    def setUp(self):
        super(TestIFrameBlockBuilder, self).setUp()
        self.grant('Manager')

    @browsing
    def test_add_iframeblock(self, browser):
        content_page = create(Builder('sl content page'))
        create(Builder('iframe block')
               .titled(u'My iFrame block')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertTrue(len(browser.css('.sl-block')), 'Expect one block')
