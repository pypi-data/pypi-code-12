# -*- coding: utf-8 -*-

from obscheme.field import Undefined
from obscheme.fields.schema_object import SchemaObjectField
from obscheme.fields.string import StringField
from obscheme.schema import Schema
from obscheme.schemameta import SchemaMeta


########################################################################
class LoginSchema(Schema):

    name = StringField()


########################################################################
class Login(object):
    __metaclass__ = SchemaMeta
    __schema__ = LoginSchema()


########################################################################
class AccountSchema(Schema):

    login = SchemaObjectField(Login)


########################################################################
class Account(object):
    __metaclass__ = SchemaMeta
    __schema__ = AccountSchema()


#----------------------------------------------------------------------
def test_schema_object_attr_undefined():
    obj = Account()
    assert isinstance(obj.login, Undefined)


#----------------------------------------------------------------------
def test_schema_object_attr_field():
    obj = Account()
    assert isinstance(obj.login.field, SchemaObjectField)


#----------------------------------------------------------------------
def test_schema_object_attr_auth_field():
    obj = Account()
    assert isinstance(obj.login.authoritative_field, SchemaObjectField)


#----------------------------------------------------------------------
def test_schema_object_attr_auth_field_has_factory():
    obj = Account()
    assert hasattr(obj.login.authoritative_field, 'factor')


#----------------------------------------------------------------------
def test_schema_object_attr_auth_field_factory():
    obj = Account()
    account = obj.login.authoritative_field.factor()
    assert isinstance(account, Login)
