"""Tests for the models of the outlets app."""
from django.test import TestCase
from django.utils.timezone import now, timedelta

from mixer.backend.django import mixer

from .. import models


class OutletManagerTestCase(TestCase):
    """Tests for the ``OutletManager`` custom manager."""
    longMessage = True

    def setUp(self):
        future_date = now() + timedelta(days=7)
        past_date = now() - timedelta(days=7)

        self.past_outlet = mixer.blend(
            'outlets.Outlet', start_date=past_date, end_date=past_date)
        self.active_outlet = mixer.blend(
            'outlets.Outlet', start_date=past_date, end_date=future_date)
        self.future_outlet = mixer.blend(
            'outlets.Outlet', start_date=future_date, end_date=future_date)
        self.no_date_outlet = mixer.blend('outlets.Outlet')
        self.no_start_outlet = mixer.blend('outlets.Outlet',
                                           start_date=past_date)
        self.no_end_outlet = mixer.blend('outlets.Outlet',
                                         end_date=future_date)
        self.ended_in_past_outlet = mixer.blend(
            'outlets.Outlet', end_date=past_date)
        self.starts_in_future_outlet = mixer.blend(
            'outlets.Outlet', start_date=future_date)

    def test_manager(self):
        self.assertEqual(models.Outlet.objects.active().count(), 4, msg=(
            'Should return the correct amount of active outlets.'))
        self.assertEqual(models.Outlet.objects.future().count(), 6, msg=(
            'Should return the correct amount of future outlets.'))


class OutletTestCase(TestCase):
    """Tests for the ``Outlet`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``Outlet`` model."""
        outlet = mixer.blend('outlets.Outlet')
        self.assertTrue(str(outlet))


class OutletCountryTestCase(TestCase):
    """Tests for the ``OutletCountry`` model class."""
    longMessage = True

    def test_instantiation(self):
        """Test instantiation of the ``OutletCountry`` model."""
        outletcountry = mixer.blend('outlets.OutletCountry')
        self.assertTrue(str(outletcountry))
