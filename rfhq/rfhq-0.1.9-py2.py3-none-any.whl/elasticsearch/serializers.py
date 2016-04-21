# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

from rest_framework.serializers import Serializer, ListSerializer


class SourceSerializer(Serializer):

    def to_representation(self, instance):
        return instance['_source']


class RoutedDocTypeMixin(object):

    def get_routing_key(self):
        return self.context.get("routing_key", None)


class DocTypeSerializer(RoutedDocTypeMixin, Serializer):

    def to_representation(self, instance):
        data = super(DocTypeSerializer, self).to_representation(instance)
        data.update(instance.to_dict())
        return data


class DocTypeListSerializer(ListSerializer):

    def to_representation(self, instance):
        return instance.to_dict()


class AggregationsSerializer(Serializer):

    pass


class AggregationSerializer(Serializer):
    """
    Substitutes aggregation bucket to search results and use them in serialization

    The paginator's results will contain the results found in Meta.aggregation_bucket_name

    """

    @classmethod
    def many_init(cls, instance=None, *args, **kwargs):

        if instance is None:
            return super(AggregationSerializer, cls).many_init(instance, *args, **kwargs)

        if not hasattr(instance, 'aggregations'):
            raise RuntimeError("No aggregations found")

        meta = getattr(cls, 'Meta', None)
        try:
            aggregation = instance.aggregations[meta.aggregation_bucket_name].buckets
            return super(AggregationSerializer, cls).many_init(aggregation, **kwargs)
        except AttributeError:
            raise RuntimeError("No aggregation_bucket_name found on serializer's Meta")
        except KeyError:
            raise RuntimeError("Aggregation bucket {} doesn't exist in aggregations".format(meta.aggregation_bucket_name))


