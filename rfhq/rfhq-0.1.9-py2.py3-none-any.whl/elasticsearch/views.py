# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response


class AggregateModelMixin(object):
    @property
    def aggregation_backends(self):
        raise NotImplementedError()

    def aggregate_queryset(self, queryset):
        for backend, nested_backends in self.aggregation_backends:
            queryset = backend(children=nested_backends).aggregate_queryset(self.request, queryset, self)
        return queryset

    def aggregate(self, request, *args, **kwargs):
        queryset = self.aggregate_queryset(self.filter_queryset(self.get_queryset()))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        data = serializer.data

        return Response(data)


class AggregateAPIView(AggregateModelMixin, GenericAPIView):
    def get(self, request, *args, **kwargs):
        return self.aggregate(request, *args, **kwargs)


class BaseAggregation(object):

    def __init__(self, children=None):
        self.children = children if children else []

    def get_aggregation_bucket(self, request, queryset, view):
        raise NotImplementedError()

    def get_children(self):
        return self.children

    def aggregate_queryset(self, request, queryset, view):
        bucket = self.get_aggregation_bucket(request, queryset, view)

        for sub_aggregration in self.get_children():
            sub_aggregration().aggregate(request, queryset, view, bucket=bucket)

        return queryset
