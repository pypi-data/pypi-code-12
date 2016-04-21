# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rfhq.mixins import NestedViewMixin


class RoutingAPIMixin(object):

    def get_routing_key(self):
        raise NotImplementedError()

    def get_serializer_context(self):
        ctx = super(RoutingAPIMixin, self).get_serializer_context()
        ctx.update({"routing_key": self.get_routing_key()})
        return ctx


class TermNestedViewMixin(NestedViewMixin):

    def filter_nested_queryset(self, queryset):
        parents_query_dict = self.get_parents_kwargs()
        if parents_query_dict:
            return queryset.filter("term", **parents_query_dict)
        else:
            return queryset


class TermNestedViewSetMixin(TermNestedViewMixin):
    pass
