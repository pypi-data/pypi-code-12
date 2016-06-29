# -*- coding: utf-8 -*-

from obscheme.field import Undefined
from obscheme.fields.string import StringField
from obscheme.schema import Schema
from obscheme.schemameta import SchemaMeta


########################################################################
class AccountSchema(Schema):

    name = StringField()


########################################################################
class Account(object):
    __metaclass__ = SchemaMeta
    __schema__ = AccountSchema()


#----------------------------------------------------------------------
def test_undefined():
    obj = Account()
    assert isinstance(obj.name, Undefined)


#----------------------------------------------------------------------
def test_undefined_has_schema_field():
    obj = Account()
    assert obj.name.field is AccountSchema.name
