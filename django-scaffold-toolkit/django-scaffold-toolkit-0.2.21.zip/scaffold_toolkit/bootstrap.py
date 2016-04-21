#coding=utf-8
from django.apps import apps
from django.conf import settings
from django.conf.urls import patterns, include, url
from importlib import import_module


def load_admins():
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.admin' % app)

        except ImportError:
            pass


def discover_admin_urls():
    """
    自动发现管理模块的url
    :return:
    """
    urlpatterns = []
    for app in settings.INSTALLED_APPS:
        try:
            import_module('%s.admin.urls' % app)
            urlpatterns += patterns("",
                                    url(r'^admin/%s/' % app, include('%s.admin.urls' % app)))
        except ImportError:
            pass
    return urlpatterns


def bootstrap():
    load_admins()