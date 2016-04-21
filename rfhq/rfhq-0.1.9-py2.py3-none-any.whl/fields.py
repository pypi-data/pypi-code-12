# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rest_framework import serializers
from rest_framework.reverse import reverse


class NestedHyperlinkedIdentityField(serializers.HyperlinkedIdentityField):

    def __init__(self, **kwargs):
        self.parents_query_lookups = kwargs.pop('parents_query_lookups')
        super(NestedHyperlinkedIdentityField, self).__init__(**kwargs)

    def get_url(self, obj, view_name, request, format):
        if obj.pk is None:
            return None
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        for lookup_url_kwarg, lookup_field in self.parents_query_lookups.items():
            lookup_value = getattr(obj, lookup_field)
            lookup_kwarg = "parent_lookup_{}".format(lookup_url_kwarg)
            kwargs.update({lookup_kwarg: lookup_value})
        return reverse(view_name, kwargs=kwargs, request=request, format=format)


