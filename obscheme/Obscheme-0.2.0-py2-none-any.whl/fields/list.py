# -*- coding: utf-8 -*-
"""
    obscheme.fields.list
    ~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from obscheme.exceptions import FieldInvalidError
from obscheme.field import Field


########################################################################
class ListFieldInvalidError(FieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, e, index):
        FieldInvalidError.__init__(self, '.'.join(e.name_stack))
        self.e = e
        self.index = index

    #----------------------------------------------------------------------
    @property
    def message(self):
        return u'{} (list index {})'.format(self.e, self.index)


########################################################################
class ListField(Field):

    #----------------------------------------------------------------------
    def __init__(self, field):
        Field.__init__(self)
        self.field = field

    #----------------------------------------------------------------------
    @property
    def authoritative_field(self):
        return self.field

    #----------------------------------------------------------------------
    def validate(self, name, values):
        for index, value in enumerate(values):
            try:
                self.field.validate(name, value)
            except Exception as e:
                raise ListFieldInvalidError(e, index)
