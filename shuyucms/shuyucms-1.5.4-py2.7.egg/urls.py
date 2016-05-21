# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.sitemaps import views as sitemaps_views
from django.views.decorators.cache import cache_page
from shuyucms.conf import settings
from shuyucms.core.sitemaps import DisplayableSitemap

try:
    from mainsys.settings import CACHE_SITEMAP_SECONDS
except ImportError:
    CACHE_SITEMAP_SECONDS = 86400

# Remove unwanted models from the admin that are installed by default with
# third-party apps.
for model in settings.ADMIN_REMOVAL:
    try:
        model = tuple(model.rsplit(".", 1))
        exec ("from %s import %s" % model)
    except ImportError:
        pass
    else:
        try:
            admin.site.unregister(eval(model[1]))
        except NotRegistered:
            pass

urlpatterns = []

# JavaScript localization feature
js_info_dict = {'domain': 'django'}
urlpatterns += patterns('django.views.i18n',
                        (r'^jsi18n/(?P<packages>\S+?)/$', 'javascript_catalog', js_info_dict),
                        )

# Django's sitemap app.
if "django.contrib.sitemaps" in settings.INSTALLED_APPS:
    sitemaps = {"sitemaps": DisplayableSitemap}
    urlpatterns += patterns('',
                            url(r'^sitemap\.xml$', cache_page(CACHE_SITEMAP_SECONDS)(sitemaps_views.index),
                                {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
                            url(r'^sitemap-(?P<section>.+)\.xml$',
                                cache_page(CACHE_SITEMAP_SECONDS)(sitemaps_views.sitemap),
                                {'sitemaps': sitemaps}, name='sitemaps'),
                            )

# Miscellanous shuyucms patterns.
urlpatterns += patterns("",
                        ("^", include("shuyucms.core.urls")),
                        ("^", include("shuyucms.generic.urls")),
                        )
