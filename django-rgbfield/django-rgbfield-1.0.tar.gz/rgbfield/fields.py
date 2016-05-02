import re

from six import string_types

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django import forms
from django.db import models

from django.utils.translation import ugettext_lazy as _


def int_to_rgb(value):
    s = hex(value)[2:]
    rem_spaces = 6 - len(s)
    if rem_spaces < 0:
        raise ValidationError(_("Invalid int for rgb color"))
    return '#' + '0' * rem_spaces + s.upper()

RGB_REGEX = re.compile('^#?((?:[0-F]{3}){1,2})$', re.IGNORECASE)


class RGBColorFormField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        kwargs['regex'] = RGB_REGEX
        super(RGBColorFormField, self).__init__(*args, **kwargs)


class RGBColorField(models.CharField):
    description = "RGB color"
    default_validators = [RegexValidator(regex=RGB_REGEX)]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(RGBColorField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RGBColorField, self).deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    @staticmethod
    def from_db_value(value, expression, connection, context):
        if value is None:
            return value

        return int_to_rgb(value)

    def to_python(self, value):
        if isinstance(value, string_types):
            return value

        if value is None:
            return value

        return int_to_rgb(value)

    def get_prep_value(self, value):
        try:
            offs = 1 if value[0] == '#' else 0
            value = value[offs:]
            # abc to aabbcc
            if len(value) == 3:
                value = ''.join(c + c for c in value)
            return int(value, 16)
        except (ValueError, IndexError):
            return None

    def formfield(self, **kwargs):
        defaults = {'form_class': RGBColorFormField}
        defaults.update(kwargs)
        return super(RGBColorField, self).formfield(**defaults)

    def get_internal_type(self):
        return "PositiveIntegerField"
