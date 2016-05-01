# -*- coding: utf-8 -*-
# ++ This file `test_utils.py` is generated at 3/7/16 6:12 PM ++
import os
import sys
from importlib import import_module
from django.test import TestCase
from hacs.models import RoutingTable
from hacs.models import SiteRoutingTable
from django.utils import six
from django.test import RequestFactory
from django.test import override_settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from django.contrib.sites.shortcuts import get_current_site
from hacs.utils import *

TEST_USER_NAME = 'test_user'
TEST_HOST_NAME = 'testserver'
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_FIXTURE = os.path.join(CURRENT_PATH, 'fixtures', 'testing_fixture.json')

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class UtilsTestCase(TestCase):
    """
    """
    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        """
        :return:
        """
        super(UtilsTestCase, self).setUp()
        self.request_factory = RequestFactory()

    def test_get_group_key(self):
        """
        :return:
        """
        user = User.objects.get(username=TEST_USER_NAME)
        request = self.request_factory.request(user=user)
        request.site = get_current_site(request)
        group = user.groups.all()[0]
        result = get_group_key(request, group, prefix='hacs')
        self.assertEqual(result, 'hacs:site_%s:group_%s' % (request.site.id, group.id))

    def test_get_user_key(self):
        """
        :return:
        """
        request = self.request_factory.request()
        request.user = user = User.objects.get(username=TEST_USER_NAME)
        request.site = get_current_site(request)
        result = get_user_key(request, prefix='hacs')
        self.assertEqual(result, 'hacs:site_%s:user_%s' % (request.site.id, user.id))

    @override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
    def test_get_generated_urlconf_file(self):
        """
        :return:
        """
        request = self.request_factory.request()
        site = get_current_site(request)
        site_route = SiteRoutingTable.objects.get(site=site)

        result = get_generated_urlconf_file(site_route.route.route_name, prefix='hacs')
        self.assertEqual(result, '/tmp/hacs_%s_urls.py' % sanitize_filename(site_route.route.route_name))

    @override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
    def test_generate_urlconf_file(self):

        request = self.request_factory.request()
        site = get_current_site(request)
        site_route = SiteRoutingTable.objects.get(site=site)
        filename = get_generated_urlconf_file(site_route.route.route_name, prefix='hacs')
        if os.path.exists(filename):
            os.unlink(filename)

        generate_urlconf_file(filename, site_route.route)
        self.assertTrue(os.path.exists(filename))

    @override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
    def test_get_generated_urlconf_module(self):

        request = self.request_factory.request()
        site = get_current_site(request)
        site_route = SiteRoutingTable.objects.get(site=site)
        filename = get_generated_urlconf_file(site_route.route.route_name, prefix='hacs')
        generate_urlconf_file(filename, site_route.route)
        sys.path.append('/tmp')
        result = get_generated_urlconf_module(filename, validation=True)
        self.assertEqual(result, 'hacs_default_route_urls')
        try:
            import_module(result)
        except ImportError:
            raise AssertionError("Code should not come here")

    def test_sanitize_filename(self):

        dirty_name = "Mকy D@-^a~d. Mam"
        expected_name = "MyD_adMam"
        result = sanitize_filename(dirty_name)

        self.assertEqual(expected_name, result)

    def test_get_installed_apps_urlconf(self):

        results = get_installed_apps_urlconf()

        # As three apps have urls (url pattern)(django.contrib.auth, django.contrib.staticfiles, hacs)
        # So results should have length 3
        self.assertEqual(3, len(results))

        hacs_urls = [x for x in results if x.app_label == 'hacs'][0]
        urlconf = import_module(hacs_urls.module)
        self.assertIsInstance(urlconf.urlpatterns, list)

        from django.core.urlresolvers import RegexURLPattern
        self.assertIsInstance(urlconf.urlpatterns[0], RegexURLPattern)

        # hacs urls has two custom handler
        self.assertEqual(2, len(hacs_urls.error_handlers))

        # Make sure exclude apps working
        results = get_installed_apps_urlconf(exclude=('staticfiles', ))
        self.assertEqual(2, len(results))

        # Make sure patterns work
        results = get_installed_apps_urlconf(r'fake')
        self.assertEqual(0, len(results))

        # Make sure json serializer works
        results = get_installed_apps_urlconf(to_json=True)
        self.assertIsInstance(results, six.string_types)

        # Make sure valid json string
        import json
        try:
            results = json.loads(results)
            self.assertEqual(3, len(results))
        except ValueError:
            raise AssertionError("Could should not come here! Most provably invalid json string")

__all__ = ['UtilsTestCase', ]
