"""
Provides the default serializer implementations that come with the module.

See the BaseSerializer documentation for details on how to implement your own.
"""

from decimal import Decimal, InvalidOperation
import re

import six

from django.core.exceptions import ValidationError


class BaseSerializer(object):
    """
    Sample class providing the serializer interface.

    You don't have to extend this class to create a valid serializer as long as your
    custom class has the following methods: serialize(val), unserialize(val), validate(val).

    The constructor should also accept the current configuration object as the first argument.
    This is useful if you want to implement a serializer whose output depends on some
    other configuration data.
    """

    def __init__(self, config):
        """
        Constructor.

        Requires an instance of aboutconfig.models.Config.
        """

        self.config = config

    @staticmethod
    def is_class_valid(klass):
        """
        Verify that the given class object has all the required methods.

        Checks for serialize, unserialize, validate.
        """

        try:
            assert hasattr(klass, 'serialize')
            assert hasattr(klass, 'unserialize')
            assert hasattr(klass, 'validate')
        except AssertionError:
            return False
        else:
            return True

    def serialize(self, val):
        """
        Convert a python value to string.

        Dummy implementation. Override in subclasses.
        """

        raise NotImplementedError()

    def unserialize(self, val):
        """
        Convert a string value to a python object.

        Dummy implementation. Override in subclasses.
        """

        raise NotImplementedError()

    def validate(self, val):
        """
        Validate a serialized value. Primarily used in forms (which return strings).

        Dummy implementation. Optionally override in subclasses.
        """

        pass


class StrSerializer(BaseSerializer):
    """Serializer for strings."""

    def serialize(self, val):
        """Does essentially nothing since the serialized value is the original value."""

        return six.text_type(val)

    def unserialize(self, val):
        """Does essentially nothing since the serialized value is the original value."""

        return six.text_type(val)


class IntSerializer(BaseSerializer):
    """Serializer for ints."""

    def serialize(self, val):
        """Convert an integer to string."""

        return six.text_type(val)

    def unserialize(self, val):
        """Convert a string representation into an integer."""

        return int(val)

    def validate(self, val):
        """
        Assert string is a valid integer representation.

        Raises ValidationError.
        """

        if not re.match(r'^-?\d+$', val):
            raise ValidationError('Not a valid integer')


class BoolSerializer(BaseSerializer):
    """Serializer for bools."""

    def serialize(self, val):
        """Convert a boolean into a string."""

        return 'true' if val else 'false'

    def unserialize(self, val):
        """Convert a string representation into a boolean."""

        val = val.lower()
        return val == 'true'

    def validate(self, val):
        """
        Assert string is a valid boolean representation.

        Raises ValidationError.
        """

        if val.lower() not in ('true', 'false'):
            raise ValidationError('Must be "true" or "false"')


class DecimalSerializer(BaseSerializer):
    """Serializer for decimal.Decimal objects."""

    def serialize(self, val):
        """Convert a decimal object into a string."""

        return six.text_type(val)

    def unserialize(self, val):
        """Convert a string representation into a decimal object."""

        return Decimal(val)

    def validate(self, val):
        """
        Assert string is a valid decimal representation.

        Raises ValidationError.
        """

        try:
            Decimal(val)
        except InvalidOperation:
            raise ValidationError('Not a valid decimal')
