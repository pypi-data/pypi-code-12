# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rest_framework.relations import HyperlinkedIdentityField


class HyperlinkedIdentityWithParamsField(HyperlinkedIdentityField):

    def __init__(self, view_name=None, **kwargs):
        self.view_kwargs = kwargs.pop('view_kwargs', {})
        super(HyperlinkedIdentityWithParamsField, self).__init__(view_name, **kwargs)

    def get_url(self, obj, view_name, request, format):
        if obj.pk is None:
            return None
        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        kwargs.update(**self.view_kwargs)
        return self.reverse(view_name, kwargs=kwargs, request=request, format=format)
