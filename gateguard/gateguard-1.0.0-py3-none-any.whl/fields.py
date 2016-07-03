# coding=utf-8

import re
import json
import urllib.parse

from .exceptions import ValidationError


class Field(object):

    default_error_messages = {
        'required': 'Value is required',
        'invalid': 'Value is invalid',
    }

    def __init__(self, *, required=True, default=None,
                 validators=None, error_messages=None):

        """Initialization instance.

        :param required (optional): value is required flag.
        :type required: bool.
        :param default (optional): default value.
        :type default: type.
        :param validators (optional): additional validators.
        :type validators: iterable of callable.
        :param error_messages (optional): custom error messages.
        :type error_messages: dict.
        """

        self.required = required
        self.default = default
        self.validators = validators or []

        messages = {}

        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))

        messages.update(error_messages or {})

        self.error_messages = messages

    def validate(self, value=None):
        value = value or self.default

        if value is None:
            if self.required:
                self.fail('required')
            else:
                return None

        value = self.to_internal_value(value)

        self.is_valid(value)

        for validator in self.validators:
            validator(value)

        return value

    def fail(self, error_code):
        raise ValidationError(self.error_messages[error_code].format(self))

    def is_valid(self, value):
        raise NotImplementedError()

    def to_representation(self, value):
        return value

    def to_internal_value(self, value):
        return value


class TypedField(Field):

    default_error_messages = {
        'invalid': 'Value must be a valid {0.type.__name__}'
    }

    def is_valid(self, value):
        if not isinstance(value, self.type):
            self.fail('invalid')


class BooleanField(TypedField):

    type = bool
    default_error_messages = {
        'invalid': 'Value must be a valid boolean'
    }


class StringField(TypedField):

    type = str
    default_error_messages = {
        'invalid': 'Value must be a valid string',
        'min_length': 'String must be greater {0.min_length} characters',
        'max_length': 'String must be less {0.max_length} characters'
    }

    def __init__(self, *, min_length=None, max_length=None, **kwargs):
        self.min_length = min_length
        self.max_length = max_length
        super().__init__(**kwargs)

    def is_valid(self, value):
        super().is_valid(value)

        if self.min_length is not None and len(value) < self.min_length:
            self.fail('min_length')

        if self.max_length is not None and len(value) > self.max_length:
            self.fail('max_length')


class NumericField(TypedField):

    default_error_messages = {
        'invalid': 'Value must be a valid integer or float',
        'min_value': 'Number must be greater {0.min_value} characters',
        'max_value': 'Number must be less {0.max_value} characters'
    }

    def __init__(self, *, min_value=None, max_value=None, **kwargs):
        self.min_value = min_value
        self.max_value = max_value
        super().__init__(**kwargs)

    def to_internal_value(self, value):
        try:
            return self.type(value)
        except (TypeError, ValueError):
            self.fail('invalid')

    def is_valid(self, value):
        super().is_valid(value)

        if self.min_value is not None and value < self.min_value:
            self.fail('min_value')

        if self.max_value is not None and value > self.max_value:
            self.fail('max_value')


class IntegerField(NumericField):

    type = int
    default_error_messages = {
        'invalid': 'Value must be a valid integer',
    }


class FloatField(NumericField):

    type = float
    default_error_messages = {
        'invalid': 'Value must be a valid float',
    }


class ChoiceField(Field):

    default_error_messages = {
        'invalid': 'Value must be in {0.choices}',
    }

    def __init__(self, *, choices, **kwargs):
        """Initialization instance.

        :param choices: choices.
        :type choices: iterable.
        """
        self.choices = list(choices)
        super().__init__(**kwargs)

    def is_valid(self, value):
        if value not in self.choices:
            self.fail('invalid')


class ArrayField(TypedField):

    type = list
    default_error_messages = {
        'invalid': 'Value must be a valid array',
    }

    def __init__(self, *, field=None, **kwargs):
        self.field = field
        super().__init__(**kwargs)

    def to_internal_value(self, value):
        super().is_valid(value)

        if self.field:
            values = []
            errors = []

            for item in value:
                try:
                    values.append(self.field.to_internal_value(item))
                except ValidationError as e:
                    errors.append(e.error)

            if errors:
                raise ValidationError(errors)

            return values

        return value

    def is_valid(self, value):
        super().is_valid(value)

        if self.field:
            for item in value:
                self.field.validate(item)


class MultipleChoiceField(ArrayField, ChoiceField):

    default_error_messages = {
        'choices': 'All values must be in {0.choices}',
    }

    def __init__(self, **kwargs):
        ChoiceField.__init__(self, **kwargs)
        ArrayField.__init__(self, **kwargs)

    def is_valid(self, value):
        ArrayField.is_valid(self, value)

        if any(choice not in self.choices for choice in value):
            self.fail('choices')


class URLField(StringField):

    default_error_messages = {
        'url': 'Value must be a valid URL',
    }

    def is_valid(self, value):
        super().is_valid(value)

        url = urllib.parse.urlparse(value)

        if not (url.scheme and url.netloc):
            self.fail('url')


class RegexMatchField(StringField):

    default_error_messages = {
        'pattern': 'Value must match by {0.pattern}',
    }

    def __init__(self, *, pattern=None, **kwargs):
        self.pattern = re.compile(pattern or self.pattern)
        super().__init__(**kwargs)

    def is_valid(self, value):
        super().is_valid(value)

        if not self.pattern.match(value):
            self.fail('pattern')


class HostField(RegexMatchField):

    default_error_messages = {
        'pattern': 'Value must be a valid host',
    }
    pattern = (
        # domain
        r'(?:[\w](?:[\w-]{0,61}[\w])?\.)+'
        r'(?:[A-Za-z]{2,6}\.?|[\w-]{2,}\.?$)'
        # ipv4 address
        r'|^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    )


class SlugField(RegexMatchField):

    default_error_messages = {
        'pattern': 'Value must be a valid slug',
    }
    pattern = r'^[a-z\d\-_]+$'


class MapField(Field):

    default_error_messages = {
        'invalid': 'Value must be a map or JSON string',
    }

    def to_internal_value(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (ValueError, TypeError):
                self.fail('invalid')

        return value

    def is_valid(self, value):
        if not isinstance(value, dict):
            self.fail('invalid')
