"""Tests for the views of the ``server_guardian`` app."""
import os
import subprocess

from django.core.urlresolvers import reverse
from django.test import TestCase

from django_libs.tests.mixins import ViewRequestFactoryTestMixin
from mixer.backend.django import mixer
from mock import MagicMock

from .. import views


class GuardianDashboardViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``GuardianDashboardView`` view class."""
    view_class = views.GuardianDashboardView

    def setUp(self):
        self.user = mixer.blend('auth.User')
        self.admin = mixer.blend('auth.User', is_superuser=True)

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.is_callable(user=self.admin)
        self.redirects(user=self.user, to='{0}?next={1}'.format(
            self.get_login_url(), self.get_url()))


class GuardianReloadViewTestCase(ViewRequestFactoryTestMixin, TestCase):
    """Tests for the ``GuardianReloadView`` view class."""
    view_class = views.GuardianReloadView

    def setUp(self):
        self.user = mixer.blend('auth.User')
        self.admin = mixer.blend('auth.User', is_superuser=True)
        self.popen = subprocess.Popen
        self.exists = os.path.exists

    def tearDown(self):
        subprocess.Popen = self.popen
        os.path.exists = self.exists

    def test_view(self):
        self.should_redirect_to_login_when_anonymous()
        self.redirects(user=self.user, to='{0}?next={1}'.format(
            self.get_login_url(), self.get_url()))
        self.redirects(
            user=self.admin, to=reverse('server_guardian_dashboard'))
        self.is_callable(user=self.admin, ajax=True)

        os.path.exists = MagicMock(return_value=True)
        self.is_postable(user=self.admin, data={}, ajax=True)

        os.path.exists = MagicMock(return_value=False)
        subprocess.Popen = MagicMock()
        self.is_postable(user=self.admin, data={}, ajax=True)

        def exception():
            raise Exception('Foobar')
        subprocess.Popen = MagicMock(side_effect=exception)
        self.is_postable(user=self.admin, data={}, ajax=True)
