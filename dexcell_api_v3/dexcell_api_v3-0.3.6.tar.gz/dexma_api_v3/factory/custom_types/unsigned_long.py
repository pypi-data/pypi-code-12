__author__ = 'dcortes'

from schematics.exceptions import ValidationError
from schematics.types import BaseType


class UnsignedLong(BaseType):

    def to_native(self, value):
        if type(value) not in [long, int] and value <= 0:
            raise ValidationError("Value must be a valid unsigned long")
        return value