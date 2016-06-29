# -*- coding: utf-8 -*-
"""
    obscheme.fields.integer
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from obscheme.exceptions import WrongTypeError, FieldInvalidError
from obscheme.field import Field


########################################################################
class IntegerFieldInvalidError(FieldInvalidError):
    pass


########################################################################
class IntegerValueBelowMinError(IntegerFieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, name, value, min_value):
        IntegerFieldInvalidError.__init__(self, name)
        self.value = value
        self.min_value = min_value

    #----------------------------------------------------------------------
    @property
    def message(self):
        return u'Field value {} is lower than min {}'.format(self.value, self.min_value)


########################################################################
class IntegerValueAboveMaxError(IntegerFieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, name, value, max_value):
        IntegerFieldInvalidError.__init__(self, name)
        self.value = value
        self.max_value = max_value

    #----------------------------------------------------------------------
    @property
    def message(self):
        return u'Field value {} is higher than max {}'.format(self.value, self.max_value)


########################################################################
class IntegerField(Field):

    #----------------------------------------------------------------------
    def __init__(self, min_value=None, max_value=None):
        Field.__init__(self)
        self.min_value = min_value
        self.max_value = max_value

    #----------------------------------------------------------------------
    def validate(self, name, value):
        self._assert_is_integer_type(name, value)
        if self._min_value_given():
            self._assert_value_not_below_min(name, value)
        if self._max_value_given():
            self._assert_value_not_above_max(name, value)

    #----------------------------------------------------------------------
    def _assert_is_integer_type(self, name, value):
        if not isinstance(value, (int, long)):
            raise WrongTypeError(
                name,
                type(value),
                [int, long])

    #----------------------------------------------------------------------
    def _min_value_given(self):
        return self.min_value is not None

    #----------------------------------------------------------------------
    def _assert_value_not_below_min(self, name, value):
        if value < self.min_value:
            raise IntegerValueBelowMinError(name, value, self.min_value)

    #----------------------------------------------------------------------
    def _max_value_given(self):
        return self.max_value is not None

    #----------------------------------------------------------------------
    def _assert_value_not_above_max(self, name, value):
        if value > self.max_value:
            raise IntegerValueAboveMaxError(name, value, self.max_value)
