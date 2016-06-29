# -*- coding: utf-8 -*-
"""
    obscheme.fields.nillable
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from obscheme.exceptions import FieldInvalidError
from obscheme.field import Field


########################################################################
class NillableFieldInvalidError(FieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, e):
        FieldInvalidError.__init__(self, '.'.join(e.name_stack))
        self.e = e

    #----------------------------------------------------------------------
    def __str__(self):
        return u'{} (may be None)'.format(self.e)


########################################################################
class NillableField(Field):

    #----------------------------------------------------------------------
    def __init__(self, field):
        Field.__init__(self)
        self.field = field

    #----------------------------------------------------------------------
    @property
    def authoritative_field(self):
        return self.field

    #----------------------------------------------------------------------
    def validate(self, name, value):
        if value is not None:
            try:
                self.field.validate(name, value)
            except FieldInvalidError as e:
                raise NillableFieldInvalidError(e)
