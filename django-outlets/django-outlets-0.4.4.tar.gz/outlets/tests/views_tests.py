"""Tests for the views of the outlets app."""
from django.test import TestCase

from django_libs.tests.mixins import ViewRequestFactoryTestMixin

from mixer.backend.django import mixer

from .. import views


class OutletsListViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``OutletsListView`` view class."""
    view_class = views.OutletsListView

    def get_view_name(self):
        return 'outlets_list'

    def get_view_kwargs(self):
        return {'slug': self.country.slug}

    def setUp(self):
        self.country = mixer.blend('outlets.OutletCountry')

    def test_view(self):
        self.is_callable()

        self.redirects(kwargs={}, to=self.get_url(), msg=(
            'Should redirect to the first country if called without slug.'))

        self.is_not_callable(kwargs={
            'slug': 'not-callable-if-country-doesnt-exist'})

        self.country.delete()
        # shouldn't be callable if no country exists at all
        self.is_not_callable(kwargs={})


class MapMarkerInfoboxAJAXViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``MapMarkerInfoboxAJAXView`` view class."""
    view_class = views.MapMarkerInfoboxAJAXView

    def get_view_kwargs(self):
        return {'pk': self.outlet.pk}

    def setUp(self):
        self.outlet = mixer.blend('outlets.Outlet')

    def test_view(self):
        self.is_not_callable()
        self.is_callable(ajax=True)
