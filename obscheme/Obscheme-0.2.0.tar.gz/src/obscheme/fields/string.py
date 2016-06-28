# -*- coding: utf-8 -*-
"""
    obscheme.fields.string
    ~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from obscheme.exceptions import FieldInvalidError, WrongTypeError
from obscheme.field import Field


########################################################################
class StringFieldInvalidError(FieldInvalidError):
    pass


########################################################################
class StringTooShortError(StringFieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, name, length, min_length):
        StringFieldInvalidError.__init__(self, name)
        self.length = length
        self.min_length = min_length

    #----------------------------------------------------------------------
    @property
    def message(self):
        return u'Field length {} is lower than required {}'.format(self.length, self.min_length)


########################################################################
class StringTooLongError(StringFieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, name, length, max_length):
        StringFieldInvalidError.__init__(self, name)
        self.length = length
        self.max_length = max_length

    #----------------------------------------------------------------------
    @property
    def message(self):
        return u'Field length {} is longer than limit {}'.format(self.length, self.max_length)


########################################################################
class StringField(Field):

    #----------------------------------------------------------------------
    def __init__(self, min_length=None, max_length=None):
        Field.__init__(self)
        self.min_length = min_length
        self.max_length = max_length

    #----------------------------------------------------------------------
    def validate(self, name, value):
        self._assert_is_string_type(name, value)
        if self._min_length_given():
            self._assert_string_long_enough(name, value)
        if self._max_length_given():
            self._assert_string_short_enough(name, value)

    #----------------------------------------------------------------------
    def _assert_is_string_type(self, name, value):
        if not isinstance(value, basestring):
            raise WrongTypeError(name, type(value), basestring)

    #----------------------------------------------------------------------
    def _min_length_given(self):
        return self.min_length is not None

    #----------------------------------------------------------------------
    def _assert_string_long_enough(self, name, value):
        string_length = len(value)
        if string_length < self.min_length:
            raise StringTooShortError(name, string_length, self.min_length)

    #----------------------------------------------------------------------
    def _max_length_given(self):
        return self.max_length is not None

    #----------------------------------------------------------------------
    def _assert_string_short_enough(self, name, value):
        string_length = len(value)
        if string_length > self.max_length:
            raise StringTooLongError(name, string_length, self.max_length)
