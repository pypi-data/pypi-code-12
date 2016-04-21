# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from collections import OrderedDict
from rest_framework.serializers import Serializer


class DataFrameSerializer(Serializer):

    def to_representation(self, instance):
        data = instance.to_dict('records')
        items = [
            ('count', len(data)),
            ('next', None),
            ('previous', None),
            ('results', data),
        ]
        return OrderedDict(items)
