__author__ = 'dcortes'

import arrow
from schematics.types import BaseType


class DateISO3601Type(BaseType):

    def to_native(self, value):
        if value is None: return None
        return arrow.get(value).datetime