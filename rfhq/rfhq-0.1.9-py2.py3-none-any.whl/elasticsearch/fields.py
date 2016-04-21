# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

from collections import OrderedDict
from django.utils import six

from rest_framework.serializers import Serializer
from rest_framework.fields import Field, ChoiceField


class DateHistogramAggregationField(Field):

    def to_bucket_representation(self, bucket):
        return {"date": bucket['key_as_string'], "count": bucket['doc_count']}

    def to_representation(self, value):
        return (self.to_bucket_representation(bucket) for bucket in value['buckets'])


class GeoHashAggregationField(Field):

    def to_representation(self, value):
        return (self.to_bucket_representation(bucket) for bucket in value['buckets'])


class StatsAggregationField(Serializer):

    def to_representation(self, instance):
        return instance.to_dict()


class GeoBoundsAggregationField(Serializer):

    def to_representation(self, value):
        bounds = getattr(value, 'bounds', None)
        if bounds:
            return [bounds['top_left']['lon'], bounds['top_left']['lat']] + [bounds['bottom_right']['lon'], bounds['bottom_right']['lat']]
        return None


class DocTypeField(Field):

    def to_representation(self, value):
        return value.to_dict()


class GeoPointField(Field):

    def to_representation(self, value):
        return tuple(value['geopoint'])


class MappedChoiceField(ChoiceField):

    def __init__(self, *args, **kwargs):
        super(MappedChoiceField, self).__init__(*args, **kwargs)
        self.choice_strings_to_values = dict([
            (six.text_type(key), value) for key, value in self.choices.iteritems()
        ])


class MaxAggregationField(Field):

    def to_representation(self, value):
        return value['value']


class TermsAggregationField(Field):

    def __init__(self, key_mapping={}, *args, **kwargs):
        self.key_mapping = key_mapping
        super(TermsAggregationField, self).__init__(*args, **kwargs)

    def to_bucket_representation(self, bucket_name, bucket):
        return self.key_mapping.get(bucket_name, bucket_name), bucket.doc_count

    def to_representation(self, value):
        return OrderedDict(self.to_bucket_representation(bucket.key, bucket) for bucket in value.buckets)


class RangeAggregationField(Field):

    def to_bucket_representation(self, bucket_name, bucket):
        return bucket_name, bucket['doc_count']

    def to_representation(self, value):
        return OrderedDict(self.to_bucket_representation(bucket_name, bucket) for bucket_name, bucket in value.buckets.to_dict().iteritems())



class TopHitsAggregationField(Field):

    def __init__(self, hit_serializer, *args, **kwargs):
        self.hit_serializer = hit_serializer
        super(TopHitsAggregationField, self).__init__(*args, **kwargs)

    def to_hit_representation(self, hit):
        return self.hit_serializer(hit).data

    def to_representation(self, value):
        return OrderedDict((
            ("count", value.hits.total),
            ("results", (self.to_hit_representation(hit['_source']) for hit in value.hits.hits)),
        ))
