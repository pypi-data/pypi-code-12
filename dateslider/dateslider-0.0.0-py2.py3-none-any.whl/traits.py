from datetime import datetime

import six

from dateutil import parser

from traitlets import TraitType


class Date(TraitType):
    """A trait for dates."""

    default_value = None
    info_text = 'a datetime'

    def validate(self, obj, value):
        if isinstance(value, datetime):
            return value

        if isinstance(value, six.text_type):
            return parser.parse(value)

        self.error(obj, value)
