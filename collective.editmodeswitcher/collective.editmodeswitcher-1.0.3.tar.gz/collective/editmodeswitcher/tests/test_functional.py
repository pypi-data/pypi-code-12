from collective.editmodeswitcher.tests import FunctionalTestCase
from ftw.testbrowser import browser
from ftw.testbrowser import browsing


class TestIntegration(FunctionalTestCase):

    def is_editable(self):
        return len(browser.css('.documentEditable')) > 0

    @browsing
    def test_toggling_edit_mode(self, browser):
        self.grant('Manager')
        # The plone site should be "editable" by default for the site owner.
        browser.login().visit()
        self.assertTrue(
            self.is_editable(),
            'No ".documentEditable" found on site root. Markup changed?')

        # When we hit the "switch-editmode" view we are redirected back
        # to the context's default view:
        browser.visit(view='@@switch-editmode')
        self.assertEqual(
            self.portal.absolute_url(), browser.url,
            'Expected to be redirected to the context\'s default view but'
            ' (site root in this case) but was not.')

        # and now the document is no longer editable:
        self.assertFalse(self.is_editable(), 'Site root still editable.')

        # even when reloading:
        browser.visit()
        self.assertFalse(self.is_editable(),
                         'Editable switch not persistent?')

        # when switching back on we are redirected to the default view again:
        browser.visit(view='@@switch-editmode')
        self.assertEqual(
            self.portal.absolute_url(), browser.url,
            'Redirect seems to be wrong when re-enabling edit mode.')

        # and it is now editable again:
        self.assertTrue(self.is_editable(),
                        'Re-enabling the edit mode is not working.')

    @browsing
    def test_get_state_returns_enabled_by_default(self, browser):
        browser.login()
        self.assertEquals(
            'enabled',
            browser.visit(view='@@switch-editmode/get_state').contents)

    @browsing
    def test_get_state_returns_disabled_after_switching(self, browser):
        browser.login()
        browser.visit(view='@@switch-editmode')

        self.assertEquals(
            'disabled',
            browser.visit(view='@@switch-editmode/get_state').contents)

        browser.visit(view='@@switch-editmode')
        self.assertEquals(
            'enabled',
            browser.visit(view='@@switch-editmode/get_state').contents)
