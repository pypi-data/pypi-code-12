# -*- coding: utf-8 -*-
"""
    obscheme.fields.schema_object
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""

from obscheme.exceptions import FieldInvalidError, ValidationError
from obscheme.field import Field


########################################################################
class SchemaObjectFieldInvalidError(FieldInvalidError):

    #----------------------------------------------------------------------
    def __init__(self, e):
        FieldInvalidError.__init__(self, '.'.join(e.name_stack))
        self.e = e

    #----------------------------------------------------------------------
    def __str__(self):
        return u'{} (may be None)'.format(self.e)


########################################################################
class SchemaObjectField(Field):

    #----------------------------------------------------------------------
    def __init__(self, cls):
        Field.__init__(self)
        self.cls = cls

    #----------------------------------------------------------------------
    def factor(self, *a, **kw):
        return self.cls(*a, **kw)

    #----------------------------------------------------------------------
    def validate(self, name, value):
        if value is not None:
            try:
                self.field.validate(name, value)
            except ValidationError as e:
                raise SchemaObjectFieldInvalidError(e)
