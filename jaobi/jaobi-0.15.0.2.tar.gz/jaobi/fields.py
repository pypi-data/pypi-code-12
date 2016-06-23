# -*- coding: utf-8 -*-

from mongoengine.fields import StringField, URLField
from jaobi import utils


class SanitizedStringField(StringField):

    """ StringField without html and odd quotation marks
    """

    def __set__(self, instance, value):
        ret = super().__set__(instance, value)
        strdata = instance._data.get(self.name)

        if not strdata:
            return ret

        sanitized = utils.sanitize_string(strdata)
        instance._data[self.name] = sanitized
        return sanitized


class ImageURLField(URLField):

    """ URLField that changes a empty string to None to avoid
    ValidationError on mongoengine."""

    def __set__(self, instance, value):
        if not value:
            value = None
            instance._data[self.name] = None

        return super().__set__(instance, value)
