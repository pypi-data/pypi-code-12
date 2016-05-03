__author__ = 'dcortes'

from schematics.exceptions import ValidationError
from schematics.types import BaseType


class NullableStringType(BaseType):

    def to_native(self, value):
        if value is None:
            return value
        elif type(value) not in [str, unicode]:
            raise ValidationError("Value must be a valid string or just None")
        return value