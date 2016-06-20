from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.iframeblock.tests import FunctionalTestCase


class TestIFrameBlock(FunctionalTestCase):

    def setUp(self):
        super(TestIFrameBlock, self).setUp()
        self.grant('Manager')

    @browsing
    def test_block_url_is_parsed_to_iframe_tag_correctly(self, browser):
        """
        This test makes sure that the url passed to the creation form is added
        to the iframe tag correctly.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('iframe block')
               .having(url=u'http://www.google.com')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            u'http://www.google.com',
            browser.css('iframe.iframeblock').first.attrib['src']
        )

    @browsing
    def test_height_field_is_used_if_auto_size_is_not_set(self, browser):
        """
        This test makes sure that the url passed to the creation form is added
        to the iframe tag correctly.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('iframe block')
               .having(url=u'http://www.google.com')
               .having(height=u'400')
               .having(auto_size=False)
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            u'400',
            browser.css('iframe.iframeblock').first.attrib['height']
        )

    @browsing
    def test_scrolling_always_set_to_no(self, browser):
        """
        This test makes sure that the url passed to the creation form is added
        to the iframe tag correctly.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('iframe block')
               .having(url=u'http://www.google.com')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            'no',
            browser.css('iframe.iframeblock').first.attrib['scrolling']
        )
