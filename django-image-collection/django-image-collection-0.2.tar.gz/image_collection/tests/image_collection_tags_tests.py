"""Tests for the ``image_collection_tags`` template tags."""
from django.test import TestCase
from mixer.backend.django import mixer
from ..templatetags.image_collection_tags import render_bs3_carousel


class RenderBS3CarouselTestCase(TestCase):
    """Test case for the ``render_bs3_carousel`` template tag."""

    def test_context(self):
        """
        Test if the context of ``render_bs3_carousel`` is set up correctly.

        """
        self.assertIsNone(
            render_bs3_carousel({}, 'foobar')['collection'],
            msg=(
                'When there is no collection with the given identifier, the'
                ' collection inside the context should be "None".'
            ))
        collection = mixer.blend(
            'image_collection.ImageCollection',
            identifier='foobar')
        self.assertEqual(
            render_bs3_carousel({}, 'foobar')['collection'],
            collection,
            msg=(
                'When there is a collection with the given identifier, it'
                ' should appear in the context.'
            )
        )
