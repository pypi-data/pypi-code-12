# -*- coding: utf-8 -*-
# ++ This file `test_middleware.py` is generated at 3/7/16 6:11 PM ++
import os
import sys
import hashlib
import datetime
from importlib import import_module
from django.conf import settings
from django.utils import timezone
from django.test import Client
from django.test import TestCase
from django.test import RequestFactory
from django.test import override_settings
from django.test import modify_settings
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches

from hacs.models import RoutingTable
from hacs.models import SiteRoutingTable
from hacs.globals import HACS_SITE_CACHE

from hacs.utils import set_site_urlconf
from hacs.utils import generate_urlconf_file

from hacs.middleware import UserModel
from hacs.middleware import FirewallMiddleware
from hacs.models import ContentTypeRoutingTable
from hacs.middleware import DynamicRouteMiddleware

from hacs.lru_wrapped import get_site_urlconf
from hacs.lru_wrapped import get_group_key
from hacs.lru_wrapped import get_user_key
from hacs.lru_wrapped import get_generated_urlconf_file
from hacs.lru_wrapped import get_generated_urlconf_module
from hacs.lru_wrapped import clean_all_lru_caches

from hacs.defaults import HACS_CACHE_SETTING_NAME
from hacs.defaults import HACS_FALLBACK_URLCONF

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

sys.path.append('/tmp')

TEST_USER_NAME = 'test_user'
TEST_USER_EMAIL = 'test_user@test.co'
TEST_USER_PASSWORD = 'top_secret'
TEST_HOST_NAME = 'testserver'
TEST_ROUTE_NAME = 'default-route'
TEST_USER_ROUTE_NAME = 'user-route'
TEST_GROUP_ROUTE_NAME = 'group-route'
TEST_FALLBACK_URLCONF = 'hacs.urls'
CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_FIXTURE = os.path.join(CURRENT_PATH, 'fixtures', 'testing_fixture.json')

def clean_lru():
    get_site_urlconf.cache_clear()
    clean_all_lru_caches()


@override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
class TestMiddlewareFunction(TestCase):

    fixtures = (TEST_FIXTURE, )

    def setUp(self):

        super(TestMiddlewareFunction, self).setUp()
        self.request_factory = RequestFactory()
        HACS_SITE_CACHE.clear()
        # Let's clear the lru cache, as this function wrapped by lru_cache decorator
        clean_lru()

    def test_set_site_urlconf(self):

        request = self.request_factory.request()
        request.site = get_current_site(request)
        urlconf_filename = get_generated_urlconf_file(TEST_ROUTE_NAME)
        if os.path.exists(urlconf_filename):
            os.unlink(urlconf_filename)
        set_site_urlconf(site=request.site)
        # urlconf module created
        self.assertTrue(os.path.exists(urlconf_filename))

        urlconf_file_creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(urlconf_filename))
        set_site_urlconf(site=request.site)

        # Make sure urlconf file is not recreated
        self.assertEqual(urlconf_file_creation_time, datetime.datetime.fromtimestamp(os.path.getmtime(urlconf_filename)))

        site_route = SiteRoutingTable.objects.get(site=request.site)
        site_route.route.updated_on = timezone.now()
        site_route.route.save()
        set_site_urlconf(site=request.site)

        # Make sure urlconf file recreated, after route modification
        self.assertNotEqual(urlconf_file_creation_time,
                            datetime.datetime.fromtimestamp(os.path.getmtime(urlconf_filename)))

    def test_get_site_urlconf(self):

        request = self.request_factory.request()
        request.site = get_current_site(request)
        urlconf_filename = get_generated_urlconf_file(TEST_ROUTE_NAME)

        urlconf_module = get_site_urlconf(request.site)
        import importlib
        try:
            importlib.import_module(urlconf_module)
        except ImportError:
            raise AssertionError("Code should not come here. `%s` is not valid module or not is sys path")

        # Make sure Site Cache is updated
        self.assertEqual(1, len(HACS_SITE_CACHE))
        # We will make sure that again call will server from cache
        urlconf_file_creation_time = datetime.datetime.fromtimestamp(os.path.getmtime(urlconf_filename))

        site_route = SiteRoutingTable.objects.get(site=request.site)
        site_route.route.updated_on = timezone.now()
        site_route.route.save()
        get_site_urlconf(request.site)

        # Make sure serve from cache!
        # How can we make sure?
        # We forcefully changed the updated date of route, so if `set_site_urlconf` method is called, then urlconf
        # module file must be recreated.
        self.assertEqual(urlconf_file_creation_time, datetime.datetime.fromtimestamp(os.path.getmtime(urlconf_filename)))

    def tearDown(self):

        super(TestMiddlewareFunction, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))

        HACS_SITE_CACHE.clear()


@override_settings(HACS_FALLBACK_URLCONF=TEST_FALLBACK_URLCONF)
class TestMiddlewareFunctionException(TestCase):

    def setUp(self):

        super(TestMiddlewareFunctionException, self).setUp()
        self.request_factory = RequestFactory()
        # Let's clear the lru cache, as this function wrapped by lru_cache decorator
        clean_lru()
        HACS_SITE_CACHE.clear()

    def test_set_site_urlconf(self):

        request = self.request_factory.request()
        request.site = get_current_site(request)
        set_site_urlconf(site=request.site)
        self.assertEqual(TEST_FALLBACK_URLCONF, HACS_SITE_CACHE[request.site.domain]['urlconf'])

    def tearDown(self):

        super(TestMiddlewareFunctionException, self).tearDown()
        HACS_SITE_CACHE.clear()


@modify_settings(MIDDLEWARE_CLASSES={'append': [
     'django.contrib.sites.middleware.CurrentSiteMiddleware',
     'hacs.middleware.DynamicRouteMiddleware'

]})
@override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
class TestDynamicRouteMiddleware(TestCase):

    fixtures = (TEST_FIXTURE, )

    def setUp(self):

        super(TestDynamicRouteMiddleware, self).setUp()
        self.request_factory = RequestFactory()
        clean_lru()
        HACS_SITE_CACHE.clear()

    def test_validate(self):

        request = self.request_factory.request()
        request.site = get_current_site(request)
        middleware = DynamicRouteMiddleware()

        # We make sure this DynamicRouteMiddleware installed properly
        self.assertTrue(middleware._validate)

    def test_process_request(self):

        request = self.request_factory.request()
        request.site = get_current_site(request)
        request.urlconf = None
        urlconf_filename = get_generated_urlconf_file(TEST_ROUTE_NAME)
        middleware = DynamicRouteMiddleware()
        # Make sure not from cache
        self.assertEqual(0, len(HACS_SITE_CACHE))
        # Let's clear the lru cache, as this function wrapped by lru_cache decorator
        get_site_urlconf.cache_clear()

        middleware.process_request(request)
        self.assertEqual(request.urlconf, get_generated_urlconf_module(urlconf_filename))

        # Make sure served from lru cache
        middleware.process_request(request)
        self.assertEqual(1, get_site_urlconf.cache_info().hits)

        # Even serve from Global Site Cache
        get_site_urlconf.cache_clear()
        os.unlink(urlconf_filename)
        middleware.process_request(request)

        # Make sure serve from Global Cache although lru cache is cleared
        # As set_site_urlconf function is not called, new urlrconf file is generated although it is not exist.
        self.assertFalse(os.path.exists(urlconf_filename))

    def tearDown(self):
        super(TestDynamicRouteMiddleware, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))

        HACS_SITE_CACHE.clear()


@override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
class TestDynamicRouteMiddlewareFromBrowser(TestCase):

    fixtures = (TEST_FIXTURE, )

    def setUp(self):

        super(TestDynamicRouteMiddlewareFromBrowser, self).setUp()
        self.request_factory = RequestFactory()
        clean_lru()
        HACS_SITE_CACHE.clear()
        self._refactor_fixture()

    def _refactor_fixture(self):
        """
        :return:
        """
        from django.contrib.auth.hashers import is_password_usable
        for user in UserModel.objects.all():
            if not is_password_usable(user.password):
                user.set_password(user.password)
                user.save()

    def test_process_request(self):

        with self.modify_settings(MIDDLEWARE_CLASSES={'append': [
            'django.contrib.sites.middleware.CurrentSiteMiddleware',
            'hacs.middleware.DynamicRouteMiddleware'

        ]}):
            browser = Client()
            response = browser.get('/admin/')
            expected_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_ROUTE_NAME))

            # Status code should be 302 as anonymous user
            self.assertEqual(302, response.status_code)
            # Make sure correct urlconf module
            self.assertEqual(expected_module, response.wsgi_request.urlconf)

            # Multi Site Testing
            browser = Client(SERVER_NAME='localhost')
            response = browser.get('/admin/')
            expected_module = get_generated_urlconf_module(get_generated_urlconf_file('localhost-route'))

            # Make sure another site with same settings
            self.assertEqual('localhost', response.wsgi_request.get_host())
            # Make sure correct urlconf
            self.assertEqual(expected_module, response.wsgi_request.urlconf)

            # Make sure cache also updated
            self.assertEqual(2, len(HACS_SITE_CACHE))

    def tearDown(self):

        super(TestDynamicRouteMiddlewareFromBrowser, self).tearDown()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))

        HACS_SITE_CACHE.clear()


@modify_settings(MIDDLEWARE_CLASSES={'append': [
     'django.contrib.sites.middleware.CurrentSiteMiddleware',
     'hacs.middleware.DynamicRouteMiddleware',
     'hacs.middleware.FirewallMiddleware'

]})
@override_settings(
    HACS_GENERATED_URLCONF_DIR='/tmp',
    CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache', 'LOCATION': 'hacs_middleware', }},
)
class TestFirewallMiddleware(TestCase):

    fixtures = (TEST_FIXTURE, )

    def setUp(self):

        super(TestFirewallMiddleware, self).setUp()
        self.request_factory = RequestFactory()
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        # Let's clear the lru cache, as this function wrapped by lru_cache decorator
        clean_lru()
        HACS_SITE_CACHE.clear()

    def test_validate(self):

        middleware = FirewallMiddleware()
        # Validate
        self.assertTrue(middleware._validate)

    def test_set_group_urlconf(self):

        request = self.request_factory.request()
        request.site = get_current_site(request)
        user = request.user = UserModel.objects.get(username=TEST_USER_NAME)
        middleware = FirewallMiddleware()

        middleware._set_group_urlconf(request, user.groups.get(name='administrator'))
        group_key = get_group_key(request, user.groups.get(name='administrator'))
        group_urlconf_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_GROUP_ROUTE_NAME))

        # We make sure cache is updated and right values are assigned
        self.assertEqual(group_urlconf_module, self.cache.get(group_key)['urlconf'])
        self.assertEqual(RoutingTable.objects.get(route_name=TEST_GROUP_ROUTE_NAME),
                         RoutingTable.objects.get(pk=self.cache.get(group_key)['route_id']))

    def test_calculate_user_urlconf(self):
        """
        :return:
        """
        urls_confs = []
        for route in RoutingTable.objects.all().order_by('-id'):
            if not os.path.exists(get_generated_urlconf_file(route.route_name)):
                generate_urlconf_file(get_generated_urlconf_file(route.route_name), route)
            urls_confs.append(get_generated_urlconf_module(get_generated_urlconf_file(route.route_name)))

        middleware = FirewallMiddleware()
        result = middleware._calculate_user_urlconf('/admin/', urls_confs)
        expected_urlconf = get_generated_urlconf_module(
            get_generated_urlconf_file(TEST_GROUP_ROUTE_NAME),
            RoutingTable.objects.get(route_name=TEST_GROUP_ROUTE_NAME))

        self.assertEqual(result, expected_urlconf)

    def test_set_user_urlconf(self):

        request = self.request_factory.request()
        request.path_info = u'/admin/'
        request.site = get_current_site(request)
        session = request.session = self.SessionStore(hashlib.md5('hacs').hexdigest())
        user = request.user = UserModel.objects.get(username=TEST_USER_NAME)

        middleware = FirewallMiddleware()
        request.session['settings'] = dict()
        middleware._set_user_urlconf(request)
        user_urlconf_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_USER_ROUTE_NAME))

        # We Make sure session is updated
        try:
            self.assertEqual(session['settings']['urlconf'], user_urlconf_module)
        except KeyError:
            raise AssertionError("Code should not come here")

        # Make sure cache is also updated
        user_cache_key = get_user_key(request)
        self.assertEqual(self.cache.get(user_cache_key)['urlconf'], user_urlconf_module)

        ContentTypeRoutingTable.objects.filter(content_type=ContentType.objects.get_for_model(UserModel),
                                               object_id=user.id).delete()
        request.session.clear()
        request.session['settings'] = dict()
        self.cache.clear()
        middleware._set_user_urlconf(request)

        # Make sure session updated and urlconf changed to Group Routing specific
        user_urlconf_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_GROUP_ROUTE_NAME))
        try:
            # user's urlconf should be instance of tuple, because use could be member of several groups
            self.assertEqual(session['settings']['urlconf'][0], user_urlconf_module)
        except KeyError:
            raise AssertionError("Code should not come here")

        # Make sure cache also be updated and Group specific routing
        self.assertEqual(self.cache.get(user_cache_key)['urlconf'][0], user_urlconf_module)

        ContentTypeRoutingTable.objects.filter(content_type=ContentType.objects.get_for_model(Group)).delete()

        request.session.clear()
        request.session['settings'] = dict()
        self.cache.clear()
        middleware._set_user_urlconf(request)

        # Make sure fallback urlconf is None, because request has no urlconf attribute either set by DynamicMiddleware
        # or from django settings
        try:
            # user's urlconf should be none, because either user or groups have no urlconf
            self.assertIsNone(session['settings']['urlconf'])
        except KeyError:
            raise AssertionError("Code should not come here")

    def test_process_request(self):

        request = self.request_factory.request()
        request.path_info = u'/admin/'
        request.site = get_current_site(request)
        user = request.user = UserModel.objects.get(username=TEST_USER_NAME)
        request.session = self.SessionStore(hashlib.md5(user.username).hexdigest())
        middleware = FirewallMiddleware()
        middleware.process_request(request)

        user_urlconf_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_USER_ROUTE_NAME))
        # Make sure user's urlconf module is assigned
        self.assertEqual(user_urlconf_module, request.urlconf)

        # Let's Try for Anonymous User
        request.urlconf = None
        request.user = AnonymousUser()
        self.cache.clear()
        request.session.clear()
        middleware.process_request(request)
        # Should be Fallback urlconf module
        self.assertEqual(request.urlconf, HACS_FALLBACK_URLCONF)

        ContentTypeRoutingTable.objects.filter(content_type=ContentType.objects.get_for_model(UserModel),
                                               object_id=user.id).delete()
        user_urlconf_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_GROUP_ROUTE_NAME), validation=False)
        self.cache.clear()
        request.session.clear()
        # Restore original user
        request.user = user
        middleware.process_request(request)
        # Make sure user's group's urlconf is assigned as user's routing is not available
        self.assertEqual(user_urlconf_module, request.urlconf)

        ContentTypeRoutingTable.objects.filter(content_type=ContentType.objects.get_for_model(Group)).delete()
        self.cache.clear()
        request.session.clear()
        request.urlconf = None

        middleware.process_request(request)
        # As urlconf is unavailable for user as well as groups and request urlconf attribute has None value
        # So showing warning and assign fallback urlconf
        self.assertEqual(request.urlconf, HACS_FALLBACK_URLCONF)

    def tearDown(self):

        super(TestFirewallMiddleware, self).tearDown()
        # I don't know if bellow method required or automatically cleared after tear down
        self.cache.clear()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))


@override_settings(HACS_GENERATED_URLCONF_DIR='/tmp')
class TestFirewallMiddlewareFromBrowser(TestCase):

    fixtures = (TEST_FIXTURE, )

    def setUp(self):
        super(TestFirewallMiddlewareFromBrowser, self).setUp()
        self.request_factory = RequestFactory()
        self._refactor_fixture()
        engine = import_module(settings.SESSION_ENGINE)
        self.SessionStore = engine.SessionStore
        self.cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        # Let's clear the lru cache, as this function wrapped by lru_cache decorator
        clean_lru()
        HACS_SITE_CACHE.clear()

    def _refactor_fixture(self):
        """
        :return:
        """
        from django.contrib.auth.hashers import is_password_usable
        for user in UserModel.objects.all():
            if not is_password_usable(user.password):
                user.set_password(user.password)
                user.save()

    def test_process_request(self):

        with modify_settings(
            MIDDLEWARE_CLASSES={'append': [
                'django.contrib.sites.middleware.CurrentSiteMiddleware',
                'hacs.middleware.DynamicRouteMiddleware',
                'hacs.middleware.FirewallMiddleware'
            ]}
        ):
            browser = Client()
            response = browser.get('/admin/')
            # AS anonymous user so urlconf module should default site
            expected_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_ROUTE_NAME))
            self.assertEqual(expected_module, response.wsgi_request.urlconf)
            # As anonymous user, so no direct access, should be redirected to login page
            self.assertEqual(302, response.status_code)

            browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
            response = browser.get('/admin/')
            # Authenticated admin user should have access
            self.assertEqual(200, response.status_code)

            # User has dedicated urlconf module, so it should be assigned
            expected_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_USER_ROUTE_NAME))
            self.assertEqual(expected_module, response.wsgi_request.urlconf)

            ContentTypeRoutingTable.objects.filter(content_type=ContentType.objects.get_for_model(UserModel),
                                                   object_id=response.wsgi_request.user.id).delete()

            # Make Session works, as we remove user's route but still should same
            response = browser.get('/admin/')
            self.assertEqual(expected_module, response.wsgi_request.urlconf)
            self.assertEqual(expected_module, response.wsgi_request.session['settings']['urlconf'])

            # Make sure caching works
            browser.logout()
            browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
            response = browser.get('/admin/')
            self.assertEqual(expected_module, response.wsgi_request.urlconf)

            # Now we are cleaning session and cache as well, so we expect urlconf should come group
            browser.logout()
            self.cache.clear()
            browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
            response = browser.get('/admin/')

            expected_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_GROUP_ROUTE_NAME))
            self.assertEqual(expected_module, response.wsgi_request.urlconf)

            ContentTypeRoutingTable.objects.filter(content_type=ContentType.objects.get_for_model(Group)).delete()

            # Now we are cleaning session and cache as well, group's route also clened
            # so we expect urlconf should be like site urlconf
            browser.logout()
            self.cache.clear()
            browser.login(username=TEST_USER_NAME, password=TEST_USER_PASSWORD)
            response = browser.get('/admin/')

            expected_module = get_generated_urlconf_module(get_generated_urlconf_file(TEST_ROUTE_NAME))
            self.assertEqual(expected_module, response.wsgi_request.urlconf)

    def tearDown(self):

        super(TestFirewallMiddlewareFromBrowser, self).tearDown()
        # I don't know if bellow method required or automatically cleared after tear down
        self.cache.clear()
        for root, dirs, files in os.walk(settings.HACS_GENERATED_URLCONF_DIR):
            for file_name in files:
                if file_name.startswith('hacs'):
                    os.unlink(os.path.join(root, file_name))
