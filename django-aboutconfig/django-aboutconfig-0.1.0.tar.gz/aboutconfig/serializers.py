from decimal import Decimal, InvalidOperation
import six
import re

from django.core.exceptions import ValidationError


class BaseSerializer(object):
    def __init__(self, config):
        self.config = config

    @staticmethod
    def is_class_valid(klass):
        try:
            assert hasattr(klass, 'serialize')
            assert hasattr(klass, 'unserialize')
            assert hasattr(klass, 'validate')
        except AssertionError:
            return False
        else:
            return True

    def serialize(self, val):
        raise NotImplementedError()

    def unserialize(self, val):
        raise NotImplementedError()

    def validate(self, val):
        pass


class StrSerializer(BaseSerializer):
    def serialize(self, val):
        return six.text_type(val)

    def unserialize(self, val):
        return six.text_type(val)


class IntSerializer(BaseSerializer):
    def serialize(self, val):
        return six.text_type(val)

    def unserialize(self, val):
        return int(val)

    def validate(self, val):
        if not re.match(r'^-?\d+$', val):
            raise ValidationError('Not a valid integer')


class BoolSerializer(BaseSerializer):
    def serialize(self, val):
        return 'true' if val else 'false'

    def unserialize(self, val):
        val = val.lower()
        return val == 'true'

    def validate(self, val):
        if val.lower() not in ('true', 'false'):
            raise ValidationError('Must be "true" or "false"')


class DecimalSerializer(BaseSerializer):
    def serialize(self, val):
        return six.text_type(val)

    def unserialize(self, val):
        return Decimal(val)

    def validate(self, val):
        try:
            Decimal(val)
        except InvalidOperation:
            raise ValidationError('Not a valid decimal')
