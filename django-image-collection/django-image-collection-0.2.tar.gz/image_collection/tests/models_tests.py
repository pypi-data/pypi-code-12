"""Tests for the models of the image_collection app."""
from django.test import TestCase
from django.utils.timezone import now, timedelta

from mixer.backend.django import mixer


class ImageCollectionTestCase(TestCase):
    """Tests for the ``ImageCollection`` model class."""
    longMessage = True

    def test_instantiation(self):
        image_collection = mixer.blend('image_collection.ImageCollection')
        self.assertTrue(image_collection.pk)

    def test_is_public(self):
        collection = mixer.blend('image_collection.ImageCollection')
        self.assertFalse(collection.is_public(), msg=(
            'Should return False, since there are no images in this'
            ' collection.'
        ))
        mixer.blend(
            'image_collection.ImageSlide',
            collection=collection,
            start_date=now() + timedelta(days=10),
        )
        self.assertFalse(collection.is_public(), msg=(
            'Should return False, since there is no published image.'
        ))
        mixer.blend(
            'image_collection.ImageSlide',
            collection=collection,
            end_date=now() - timedelta(days=10),
        )
        self.assertFalse(collection.is_public(), msg=(
            'Should return False, since there is no published image.'
        ))
        mixer.blend(
            'image_collection.ImageSlide',
            collection=collection,
            start_date=now() - timedelta(days=10),
            end_date=now() + timedelta(days=10),
        )
        self.assertTrue(collection.is_public(), msg=(
            'Should return True, since there is a published image in this'
            ' collection.'
        ))


class ImageSlideTestCase(TestCase):
    """Tests for the ``ImageSlide`` model class."""
    longMessage = True

    def test_instantiation(self):
        image_slide = mixer.blend('image_collection.ImageSlide')
        self.assertTrue(image_slide.pk)
