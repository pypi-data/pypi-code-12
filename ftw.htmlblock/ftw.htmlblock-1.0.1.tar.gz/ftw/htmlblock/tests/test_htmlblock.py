from ftw.builder import Builder
from ftw.builder import create
from ftw.testbrowser import browsing
from ftw.htmlblock.tests import FunctionalTestCase


class TestHtmlBlock(FunctionalTestCase):

    def setUp(self):
        super(TestHtmlBlock, self).setUp()
        self.grant('Manager')

    @browsing
    def test_block_does_not_render_title_by_default(self, browser):
        """
        This test makes sure that the block does not render its title by
        default.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('html block')
               .titled(u'Title of the HTML block')
               .having(content=u'<p>The main content of the HTML block.</p>')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            [],
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content h2')
        )
        self.assertEqual(
            ['The main content of the HTML block.'],
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content').text
        )

    @browsing
    def test_block_title_is_rendered(self, browser):
        """
        This test makes sure that the title of the block is rendered when
        told to do so.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('html block')
               .titled(u'Title of the HTML block')
               .having(show_title=True)
               .having(content=u'<p>The content is not important in this test.</p>')
               .within(content_page))

        browser.login().visit(content_page)

        self.assertEqual(
            ['Title of the HTML block'],
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content h2').text
        )

    @browsing
    def test_block_renders_hint_if_empty(self, browser):
        """
        This test makes sure that users having the permission to add HTML
        block can see a warning if the block has no content.
        """
        content_page = create(Builder('sl content page'))

        create(Builder('html block')
               .titled(u'The title of the block is irrelevant in this test.')
               .having(show_title=False)
               .having(content=u'')
               .within(content_page))

        browser.login().visit(content_page)
        self.assertEqual(
            ['This HTML block is empty. Please add some content or remove the block.'],
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content').text
        )

        # An anonymous user must not see the hint.
        browser.logout().visit(content_page)
        self.assertEqual(
            [''],
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content').text
        )

    @browsing
    def test_script_tag_is_not_escaped(self, browser):
        """
        This test makes sure that even script tags are rendered without
        being esacaped.
        """
        content_page = create(Builder('sl content page'))

        script_tag = u'<script type="text/javascript">alert("Hello World!");</script>'

        create(Builder('html block')
               .titled(u'The title of the block is irrelevant in this test.')
               .having(show_title=False)
               .having(content=script_tag)
               .within(content_page))

        browser.login().visit(content_page)
        self.assertEqual(
            script_tag,
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content').first.normalized_innerHTML
        )

    @browsing
    def test_iframe_tag_is_not_escaped(self, browser):
        """
        This test makes sure that even iframe tags are rendered without
        being esacaped.
        """
        content_page = create(Builder('sl content page'))

        iframe_tag = u'<iframe src="http://www.w3schools.com"></iframe>'

        create(Builder('html block')
               .titled(u'The title of the block is irrelevant in this test.')
               .having(show_title=False)
               .having(content=iframe_tag)
               .within(content_page))

        browser.login().visit(content_page)
        self.assertEqual(
            iframe_tag,
            browser.css('div.ftw-htmlblock-htmlblock .sl-block-content').first.normalized_innerHTML
        )
