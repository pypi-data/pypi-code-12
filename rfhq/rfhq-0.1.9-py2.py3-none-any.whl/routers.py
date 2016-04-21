# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter, SimpleRouter, Route, DynamicListRoute, DynamicDetailRoute


class EndpointRouter(SimpleRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        DynamicListRoute(
            url=r'^{prefix}{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        DynamicDetailRoute(
            url=r'^{prefix}{lookup}/{methodname}{trailing_slash}$',
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

class NestedRegistryItem(object):
    """
    From djangorestframework-extensions

    """
    def __init__(self, router, parent_prefix, parent_item=None):
        self.router = router
        self.parent_prefix = parent_prefix
        self.parent_item = parent_item

    def register(self, prefix, viewset, base_name, parents_query_lookups):
        self.router._register(
            prefix=self.get_prefix(current_prefix=prefix, parents_query_lookups=parents_query_lookups),
            viewset=viewset,
            base_name=base_name,
        )
        return NestedRegistryItem(
            router=self.router,
            parent_prefix=prefix,
            parent_item=self
        )

    def register_urls(self, prefix, urlpatterns, base_name, parents_query_lookups):
        self.router.register_urls(self.get_prefix(current_prefix=prefix, parents_query_lookups=parents_query_lookups), urlpatterns, base_name)

    def get_prefix(self, current_prefix, parents_query_lookups):
        return '{0}/{1}'.format(
            self.get_parent_prefix(parents_query_lookups),
            current_prefix
        )

    def get_parent_prefix(self, parents_query_lookups):
        prefix = '/'
        current_item = self
        i = len(parents_query_lookups) - 1
        while current_item:
            prefix = '{parent_prefix}/(?P<{parent_pk_kwarg_name}>[^/.]+)/{prefix}'.format(
                parent_prefix=current_item.parent_prefix,
                parent_pk_kwarg_name='parent_lookup_{}'.format(parents_query_lookups[i]),
                prefix=prefix
            )
            i -= 1
            current_item = current_item.parent_item
        return prefix.strip('/')


class NestableRouterMixin(object):
    """
    From django-rest-framework-extensions (but removed obsolete code that broke with newer versions of django-rest-framework)

    """
    def __init__(self, *args, **kwargs):
        super(NestableRouterMixin, self).__init__()
        self._includes = []

    def _register(self, *args, **kwargs):
        return super(NestableRouterMixin, self).register(*args, **kwargs)

    def register(self, *args, **kwargs):
        self._register(*args, **kwargs)
        return NestedRegistryItem(router=self, parent_prefix=self.registry[-1][0])

    def register_urls(self, prefix, urlpatterns, base_name):
        self._includes.append((prefix, urlpatterns, base_name))

    def get_urls(self):
        urls = super(NestableRouterMixin, self).get_urls()
        for prefix, urlpatterns, base_name in self._includes:
            urls.append(url(''.join([prefix, self.trailing_slash]), include(urlpatterns), name=base_name))
        return urls

class SimpleNestedRouter(NestableRouterMixin, SimpleRouter):

    pass


class DefaultNestedRouter(NestableRouterMixin, DefaultRouter):

    pass
