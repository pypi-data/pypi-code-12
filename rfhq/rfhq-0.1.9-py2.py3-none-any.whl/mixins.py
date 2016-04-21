from django.core.exceptions import ImproperlyConfigured
from django.http.request import QueryDict
from django.utils.decorators import classonlymethod
from django.utils.functional import cached_property
import re
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .serializers import LenientBulkCreateSerializerMixin


class LenientBulkCreateViewMixin(object):

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not isinstance(serializer, LenientBulkCreateSerializerMixin):
            raise ImproperlyConfigured("serializer_class must inherit from 'LenientBulkCreateSerializer'")
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if serializer.bulk_validation_errors:
            # Return description of item and errors but accept the rest
            return Response(serializer.bulk_validation_errors, status=status.HTTP_202_ACCEPTED, headers=headers)
        # Return empty list as it can be massively long
        return Response([], status=status.HTTP_201_CREATED, headers=headers)


class BlendedRequest(Request):

    def __init__(self, *args, **kwargs):
        params_prefix = kwargs.pop('params_prefix')
        self._params_prefix = '{}.'.format(params_prefix) if params_prefix and not params_prefix.endswith('.') else ''
        self._mapped_params = kwargs.pop('mapped_params', {}) or {}
        super(BlendedRequest, self).__init__(*args, **kwargs)

    @cached_property
    def query_params(self):
        orignal_params = super(BlendedRequest, self).query_params
        if self._params_prefix:
            params = QueryDict(mutable=True)
            params.update({k[len(self._params_prefix):]: v for k, v in orignal_params.items() if k.startswith(self._params_prefix)})
        else:
            params = super(BlendedRequest, self).query_params
        for m_k, m_v in  self._mapped_params.items():
            for o_k, o_v in orignal_params.items():
                matches = re.match(m_v, o_k)
                if matches:
                    params[''.join([m_k, (matches.group(1) if matches.lastindex >= 1 else '')])] = o_v
        return params


class BlendableViewMixin(object):

    @classonlymethod
    def blend(cls, request, params_prefix=None, mapped_params=None, *args, **kwargs):
        self = cls()
        self.cls = cls
        self.args = args
        self.kwargs = kwargs
        self.request = self.initialize_blended_request(request, params_prefix, mapped_params, *args, **kwargs)
        return self

    def initialize_blended_request(self, request, params_prefix, mapped_params, *args, **kwargs):
        return BlendedRequest(
            request,
            parsers=self.get_parsers(),
            authenticators=self.get_authenticators(),
            negotiator=self.get_content_negotiator(),
            parser_context=self.get_parser_context(request),
            params_prefix=params_prefix,
            mapped_params=mapped_params
        )

    def get_filtered_queryset(self):
        return self.filter_queryset(self.get_queryset())


class SelfLookupMixin(object):
    """
    Allows looking up objects using the 'self' keyword in urls in place of the primary key for the currently logged in user/account.

    When 'self' is found as the lookup value, it is substituted by the result of the call to get_self_lookup_value.

    When using nested routers, each key containing self is substituted by the result of the call to get_{key}_self_lookup_value.

    """
    self_pk = 'self'

    def get_self_lookup_value(self):
        raise NotImplementedError("View must implement get_self_lookup_value()")

    def initial(self, request, *args, **kwargs):
        super(SelfLookupMixin, self).initial(request, *args, **kwargs)
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        if lookup_url_kwarg in kwargs and kwargs[lookup_url_kwarg] == self.self_pk:
            self.kwargs[lookup_url_kwarg] = kwargs[lookup_url_kwarg] = self.get_self_lookup_value()

    def get_parents_kwargs(self):
        result = super(SelfLookupMixin, self).get_parents_kwargs()
        for query_lookup, query_value in result.items():
            if query_value == self.self_pk:
                if not hasattr(self, 'get_{}_self_lookup_value'.format(query_lookup)):
                        raise NotImplementedError("View must implement get_{}_self_lookup_value()".format(query_lookup))
                query_value = getattr(self, 'get_{}_self_lookup_value'.format(query_lookup))()
                result[query_lookup] = query_value
        return result


class NestedViewMixin(object):
    """
    Allows nesting a viewset under another viewset for filtered access

    From djangorestframework-extensions

    """
    def get_queryset(self):
        return self.filter_nested_queryset(super(NestedViewMixin, self).get_queryset())

    def filter_nested_queryset(self, queryset):
        parents_query_dict = self.get_parents_kwargs()
        if parents_query_dict:
            return queryset.filter(**parents_query_dict)
        else:
            return queryset

    def get_parents_kwarg(self, key, default=None):
        return self.get_parents_kwargs().get(key, default)

    def get_parents_kwargs(self):
        if hasattr(self, '_parent_kwargs'):
            return self._parent_kwargs
        result = {}
        for kwarg_name in self.kwargs:
            if kwarg_name.startswith('parent_lookup_'):
                query_lookup = kwarg_name.replace('parent_lookup_', '', 1)
                query_value = self.kwargs.get(kwarg_name)
                result[query_lookup] = query_value
        self._parent_kwargs = result
        return result

    def is_nested(self, parent_lookup_key=None):
        if parent_lookup_key:
            return "parent_lookup_{}".format(parent_lookup_key) in self.kwargs
        return any(kwarg_name.startswith('parent_lookup_') for kwarg_name in self.kwargs)


class NestedViewSetMixin(NestedViewMixin):
    pass
