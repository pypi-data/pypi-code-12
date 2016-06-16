# -*- coding: utf-8 -*-
"""Test viewlet of collective.pamfixes."""

# python imports
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# zope imports
try:
    from plone.app.multilingual.api import translate
except ImportError:
    from plone.app.multilingual.tests.utils import makeTranslation as translate

from plone.app.multilingual.browser.viewlets import AlternateLanguagesViewlet

# local imports
from collective.pamfixes import testing
from collective.pamfixes.viewlets import CustomAlternateLanguagesViewlet


class TestViewlet(unittest.TestCase):
    """Validate setup process for collective.pamfixes."""

    layer = testing.COLLECTIVE_PAMFIXES_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']

    def test_viewlet_render(self):
        """Validate that the alternate languages viewlet renders correctly."""
        try:
            from plone.app.multilingual.setuphandlers import (
                enable_translatable_behavior,
            )
        except ImportError:
            pass
        else:
            enable_translatable_behavior(self.portal)

        sample_en = self.portal['en']['sample-folder']
        sample_de = translate(sample_en, 'de')
        viewlet_orig = AlternateLanguagesViewlet(
            sample_de,
            self.app.REQUEST,
            None,
            None,
        )
        viewlet_orig.update()

        viewlet = CustomAlternateLanguagesViewlet(
            sample_de,
            self.app.REQUEST,
            None,
            None,
        )
        viewlet.update()
        self.assertTrue(len(viewlet.alternates), 3)
