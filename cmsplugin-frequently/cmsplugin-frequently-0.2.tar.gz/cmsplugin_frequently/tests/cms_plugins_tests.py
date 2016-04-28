"""Tests for models of the ``frequently``` application."""
from django.test import TestCase

from mixer.backend.django import mixer

from ..cms_plugins import CMSFrequentlyCategoryPlugin


class CMSFrequentlyCategoryPluginTestCase(TestCase):
    """Tests for the ``CMSFrequentlyCategoryPlugin`` cmsplugin."""
    longMessage = True

    def setUp(self):
        self.plugin = mixer.blend(
            'cmsplugin_frequently.FrequentlyEntryCategoryPlugin')
        self.category = mixer.blend('frequently.EntryCategory')
        self.cmsplugin = CMSFrequentlyCategoryPlugin()

    def test_render(self):
        context = self.cmsplugin.render({}, self.plugin, None)
        self.assertFalse(context['categories'], msg=(
            'Should return an empty list, if there has no category been added,'
            ' yet.'))

        self.plugin.categories.add(self.category)
        context = self.cmsplugin.render({}, self.plugin, None)
        self.assertEqual(context['categories'].count(), 1,
                         msg=('Should return selected categories.'))
