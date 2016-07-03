# coding=utf-8

import collections

from .fields import Field
from .exceptions import ValidationError


class MetaSchema(type):

    @classmethod
    def __prepare__(mcs, *args, **kwargs):
        return collections.OrderedDict()

    def __new__(mcs, name, bases, attributes):
        fields = collections.OrderedDict()

        for name, field in attributes.items():
            if isinstance(field, Field):
                fields[name] = field

        for field in fields:
            attributes.pop(field)

        cls = type.__new__(mcs, name, bases, attributes)

        cls.__fields__ = fields
        cls.ValidationError = ValidationError

        return cls


class Schema(object, metaclass=MetaSchema):

    @classmethod
    def validate(cls, data):
        errors = {}

        for name, field in cls.__fields__.items():
            try:
                value = data.get(name, field.default)
                data[name] = field.validate(value)
            except ValidationError as e:
                errors[name] = e.error

        if errors:
            raise ValidationError(errors)

        return data
