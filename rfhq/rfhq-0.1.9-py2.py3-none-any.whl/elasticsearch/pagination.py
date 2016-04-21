# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from collections import OrderedDict
from django.core.exceptions import ImproperlyConfigured
from elasticsearch.exceptions import TransportError
from rest_framework.exceptions import ParseError

from rest_framework.utils.urls import replace_query_param
from rest_framework.pagination import _positive_int
from rest_framework.pagination import _get_count, LimitOffsetPagination, BasePagination, CursorPagination
from rest_framework.response import Response


class ElasticsearchPagination(LimitOffsetPagination):

    max_limit = 200
    max_pages = 500

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        if self.limit is None:
            return None
        self.offset = self.get_offset(request)

        # try:
        results = queryset[self.offset:self.offset + self.limit].execute()
        # except TransportError:
            # raise ParseError("Invalid query or parameter value")
        self.count = results.hits.total
        if 'suggest' in results:
            self.suggestions = results.suggest.to_dict()
        else:
            self.suggestions = []
        if 'aggregations' in results:
            self.aggregations = results.aggregations.to_dict()
        else:
            self.aggregations = {}
        self.request = request
        if self.count > self.limit and self.template is not None:
            self.display_page_controls = True
        return results

    def get_paginated_response(self, data):
        items = [
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data),
        ]
        if self.suggestions:
            items.append(('suggestions', self.suggestions))
        if self.aggregations:
            items.append(('aggregations', self.aggregations))
        return Response(OrderedDict(items))

    def get_offset(self, request):
        try:
            return _positive_int(
                request.query_params[self.offset_query_param],
                cutoff=((self.limit * self.max_pages) - self.limit)
            )
        except (KeyError, ValueError):
            return 0

    def get_next_link(self):
        if self.offset + self.limit >= self.count:
            return None

        if self.offset + self.limit >= (self.max_pages * self.limit):
            return None

        url = self.request.build_absolute_uri()
        offset = self.offset + self.limit
        return replace_query_param(url, self.offset_query_param, offset)


class ElasticsearchAggregationPagination(ElasticsearchPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', None),
            ('previous', None),
            ('results', data)
        ]))
