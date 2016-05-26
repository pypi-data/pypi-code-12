from __future__ import unicode_literals

# ++ This file `fields.py` is generated at 3/4/16 5:54 PM ++
import ast
import json
from django.db import models
from django.utils import six
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder

__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"


class JsonField(models.TextField):
    """
    Idea From: https://djangosnippets.org/snippets/1478/
    """

    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        self.deserialize = kwargs.pop('deserialize', False)

        super(JsonField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """
        :param value:
        :return:
        """
        if not self.deserialize:

            return super(JsonField, self).to_python(value)

        if value == "":
            return None

        try:
            if isinstance(value, six.text_type):
                value = json.loads(value)

            elif isinstance(value, six.string_types):
                value = json.loads(smart_text(value))

        except ValueError:
            try:
                # Fallback: django serializer may cast dict or list value as string
                value = ast.literal_eval(value)
            except ValueError:
                raise
        return value

    def get_prep_value(self, value):
        """
        :param value:
        :return:
        """
        if value in('', "", True) or not value:
            return None

        value = super(JsonField, self).get_prep_value(value)
        if isinstance(value, (dict, list, set, tuple)):
            try:
                value = json.dumps(value, cls=DjangoJSONEncoder)
            except ValueError:
                raise
        return value

    def from_db_value(self, value, expression, connection, context):
        """
        :param value:
        :param expression:
        :param connection:
        :param context:
        :return:
        """
        return self.to_python(value)


class JsonDictField(JsonField):
    """
        Only allows python Dictionary data type data
    """

    def get_prep_value(self, value):

        if value in('', "", True) or not value:
            return None

        if not isinstance(value, dict):
            raise TypeError(_('Only `dict` type data is accepted but got data type `%s`' % type(value)))

        return super(JsonDictField, self).get_prep_value(value)


class JsonSequenceField(JsonField):
    """
        Only allows python list, set, tuple type data
    """

    def get_prep_value(self, value):

        if value in('', "", True) or not value:
            return None

        if not isinstance(value, (list, set, tuple)):
            raise TypeError(_('Only `list, set, tuple` type data is accepted but got data type `%s`' % type(value)))

        return super(JsonSequenceField, self).get_prep_value(value)


class DictField(JsonDictField):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        try:
            if not kwargs['deserialize']:
                kwargs['deserialize'] = True
        except KeyError:
            kwargs['deserialize'] = True

        super(DictField, self).__init__(*args, **kwargs)


class SequenceField(JsonSequenceField):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        """
        try:
            if not kwargs['deserialize']:
                kwargs['deserialize'] = True
        except KeyError:
            kwargs['deserialize'] = True

        super(SequenceField, self).__init__(*args, **kwargs)


__all__ = ('JsonField', 'JsonDictField', 'JsonSequenceField', 'DictField', 'SequenceField')
