# -*- coding: utf-8 -*-
# ++ This file `middleware.py` is generated at 3/3/16 6:05 AM ++
import logging
import warnings
from django.apps import apps
from django.utils import six
from django.conf import settings
from django.core.cache import caches
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
try:
    # expect django version 1.10.x or higher
    from django.urls import get_resolver, Resolver404
except ImportError:
    from django.core.urlresolvers import get_resolver, Resolver404
from django.utils.functional import cached_property
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from .globals import HACS_APP_NAME
from .models import ContentTypeRoutingTable
from .defaults import HACS_FALLBACK_URLCONF
from .defaults import HACS_CACHE_SETTING_NAME
from .lru_wrapped import get_user_key
from .lru_wrapped import get_group_key
from .utils import generate_urlconf_file_on_demand
from .lru_wrapped import get_generated_urlconf_file
from .lru_wrapped import get_generated_urlconf_module
from .lru_wrapped import get_site_urlconf

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

logger = logging.getLogger(u'hacs.middleware')
UserModel = get_user_model()


class DynamicRouteMiddleware(object):
    """ """
    name = 'hacs.middleware.DynamicRouteMiddleware'

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        if self._validate:
            pass

        urlconf = get_site_urlconf(getattr(request, 'site', get_current_site(request)))

        request.urlconf = urlconf

    @cached_property
    def _validate(self):
        """
        :return:
        """
        errors = []
        if not apps.is_installed(HACS_APP_NAME):
            errors.append(_("%s need to be added into settings.INSTALLED_APPS" % HACS_APP_NAME))

        if not apps.is_installed('django.contrib.contenttypes'):
            errors.append(_("django.contrib.contenttypes need to be added into settings.INSTALLED_APPS"))

        if not apps.is_installed('django.contrib.sites'):
            errors.append(_("django.contrib.sites need to be added into settings.INSTALLED_APPS"))

        try:
            site_middleware_position = \
                settings.MIDDLEWARE_CLASSES.index('django.contrib.sites.middleware.CurrentSiteMiddleware')
        except ValueError:
            errors.append(_("django.contrib.sites.middleware.CurrentSiteMiddleware need to be "
                            "added into settings.MIDDLEWARE_CLASSES"))
        else:
            if site_middleware_position > settings.MIDDLEWARE_CLASSES.index(self.name):
                errors.append(_('django.contrib.sites.middleware.CurrentSiteMiddleware\'s position should be before ' +
                                self.name))
        if errors:
            raise ImproperlyConfigured(_("Please fix: %s" % ' | '.join(errors)))

        return True


class FirewallMiddleware(object):
    """     """
    name = 'hacs.middleware.FirewallMiddleware'

    def process_request(self, request):
        """
        :param request:
        :return:
        """
        if self._validate:
            pass

        if request.user.is_authenticated():

            request_path = request.path_info
            try:
                user_settings_session = request.session['settings']
            except KeyError:
                request.session['settings'] = dict()
                user_settings_session = request.session['settings']

            try:
                user_urlconf = user_settings_session['urlconf']
            except KeyError:
                # There is no urlconf set yet! now assigning
                self._set_user_urlconf(request)
                user_urlconf = user_settings_session['urlconf']

            user_urlconf = self._calculate_user_urlconf(request_path, user_urlconf)
        else:
            # Anonymous User
            user_urlconf = self._calculate_anonymous_urlconf(request)

        if user_urlconf:
            request.urlconf = user_urlconf
        else:
            # Let's check already set by DynamicRouteMiddleware
            if not getattr(request, 'urlconf', None):
                warnings.warn("urlconf is neither set by DynamicRoutingMiddleware nor from django settings.")
                request.urlconf = getattr(settings, 'HACS_FALLBACK_URLCONF', HACS_FALLBACK_URLCONF)

    def _set_user_urlconf(self, request):
        """
        :param request:
        :return:
        """
        cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        # Try from cache
        user_settings_cache = cache.get(get_user_key(request))
        if user_settings_cache and user_settings_cache.get('urlconf', None):
            request.session['settings']['urlconf'] = user_settings_cache.get('urlconf')
            return None
        # No cache
        if not user_settings_cache:
            user_settings_cache = dict()
        try:
            user_route = ContentTypeRoutingTable.objects.get(
                site=request.site,
                content_type=ContentType.objects.get_for_model(UserModel),
                object_id=request.user.is_authenticated() and request.user.pk or 0)

        except ContentTypeRoutingTable.DoesNotExist:
            # User Has No Route Try from group
            _temp = list()
            for group in request.user.groups.all():
                group_key = get_group_key(request, group)
                # Try from cache
                group_settings_cache = cache.get(group_key, None)
                if group_settings_cache and group_settings_cache.get('urlconf', None):
                    _temp.append(group_settings_cache.get('urlconf'))
                    continue
                # Not found in cache, need to set
                self._set_group_urlconf(request, group)
                if cache.get(group_key, None).get('urlconf', None):
                    _temp.append(cache.get(group_key).get('urlconf'))
            if _temp:
                user_settings_cache['urlconf'] = tuple(_temp)
            else:
                user_settings_cache['urlconf'] = None
        else:
            # Check if urlconf file need to be created
            generate_urlconf_file_on_demand(user_route.route)
            user_settings_cache['urlconf'] = get_generated_urlconf_module(
                get_generated_urlconf_file(user_route.route.route_name))

        # Update Session
        request.session['settings'].update({'urlconf': user_settings_cache['urlconf']})
        # Set Cache
        cache.set(get_user_key(request), user_settings_cache)

    def _set_group_urlconf(self, request, group):
        """
        :param request:
        :param group:
        :return:
        """
        cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        # Try from cache
        cache_key = get_group_key(request, group)
        group_settings_cache = cache.get(cache_key)
        # No cache
        if not group_settings_cache:
            group_settings_cache = dict()
        try:
            group_route = ContentTypeRoutingTable.objects.get(
                content_type=ContentType.objects.get_for_model(Group), object_id=group.id, site=request.site)
        except ContentTypeRoutingTable.DoesNotExist:
            # We do nothing
            pass
        else:
            # we are checking if file need to be created
            generate_urlconf_file_on_demand(group_route.route)
            group_settings_cache['urlconf'] = get_generated_urlconf_module(
                get_generated_urlconf_file(group_route.route.route_name))

            group_settings_cache['route_id'] = group_route.route.pk

        # Set Cache
        cache.set(cache_key, group_settings_cache)

    @cached_property
    def _validate(self):
        """
        :return:
        """
        errors = []

        try:
            dynamic_route_middleware_position = \
                settings.MIDDLEWARE_CLASSES.index(DynamicRouteMiddleware.name)
        except ValueError:
            errors.append(_("%s need to be "
                            "added into settings.MIDDLEWARE_CLASSES" % DynamicRouteMiddleware.name))
        else:
            if dynamic_route_middleware_position > settings.MIDDLEWARE_CLASSES.index(self.name):
                errors.append(_(DynamicRouteMiddleware.name + '\'s position should be before ' +
                                self.name))
        return True

    def _calculate_user_urlconf(self, request_path, url_conf):
        """
        :param request_path:
        :param url_conf:
        :return:
        """
        if isinstance(url_conf, six.string_types):
            return url_conf
        elif isinstance(url_conf, (list, tuple, set)):
            _temp = None
            for uc in url_conf:
                try:
                    resolver = get_resolver(uc)
                    resolver.resolve(request_path)
                    _temp = uc
                    break
                except Resolver404:
                    continue
            # @TODO: need some decision what should do if result is None
            return _temp
        else:
            return None

    def _calculate_anonymous_urlconf(self, request):
        """
        """
        cache = caches[getattr(settings, 'HACS_CACHE_SETTING_NAME', HACS_CACHE_SETTING_NAME)]
        cache_key = get_user_key(request)
        user_settings = cache.get(cache_key) or dict()
        try:
            return user_settings['settings']['urlconf']
        except KeyError:
            try:
                # The hacs convention anonymous user pk is 0
                user_route = ContentTypeRoutingTable.objects.get(
                    site=request.site,
                    content_type=ContentType.objects.get_for_model(UserModel),
                    object_id=0)
                generate_urlconf_file_on_demand(user_route.route)
                urlconf = get_generated_urlconf_module(get_generated_urlconf_file(user_route.route.route_name))
            except ContentTypeRoutingTable.DoesNotExist:
                urlconf = None

            if 'settings' not in user_settings.keys():
                user_settings['settings'] = dict()
            user_settings['settings']['urlconf'] = urlconf
            # Update Cache
            cache.set(cache_key, user_settings, 3600 * 24)

            return urlconf


__all__ = ("DynamicRouteMiddleware", "FirewallMiddleware", )
