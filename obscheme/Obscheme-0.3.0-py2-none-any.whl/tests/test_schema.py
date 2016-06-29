# -*- coding: utf-8 -*-

from nose import with_setup
from nose.tools import raises

from obscheme.exceptions import WrongTypeError
from obscheme.fields.nillable import NillableField, NillableFieldInvalidError
from obscheme.fields.schema_object import SchemaObjectField
from obscheme.fields.string import StringField, StringTooLongError
from obscheme.schema import Schema
from obscheme.schemameta import schema_validate_switch, SchemaMeta


#----------------------------------------------------------------------
def enable_validation(cls):
    return lambda: schema_validate_switch(cls).enable()


########################################################################
class NoSchemaObject(object):

    #----------------------------------------------------------------------
    def __init__(self):
        self.name = None
        self.description = None
        self.sub_object = None


########################################################################
class SubTestSchema(Schema):

    name = StringField(max_length=32)


########################################################################
class SubTestObject(object):
    __metaclass__ = SchemaMeta
    __schema__ = SubTestSchema()


########################################################################
class TestSchema(Schema):

    name = StringField(max_length=32)
    description = NillableField(StringField(min_length=1))
    sub_object = NillableField(SchemaObjectField(SubTestSchema))


########################################################################
class TestObject(object):
    __metaclass__ = SchemaMeta
    __schema__ = TestSchema()


#----------------------------------------------------------------------
def test_schema_success():
    test = TestObject()
    test.name = 'name1'
    test.description = 'description1'


#----------------------------------------------------------------------
def test_schema_undefined_non_nillable():
    test = TestObject()
    test.description = 'description1'


#----------------------------------------------------------------------
@raises(WrongTypeError)
def test_schema_wrong_type():
    test = TestObject()
    test.name = 123


#----------------------------------------------------------------------
def test_schema_wrong_type_expected_types():
    test = TestObject()
    try:
        test.name = 123
    except WrongTypeError as e:
        assert e.expected_types == [basestring]


#----------------------------------------------------------------------
def test_schema_wrong_type_type():
    test = TestObject()
    try:
        test.name = 123
    except WrongTypeError as e:
        assert e.type is int


#----------------------------------------------------------------------
@with_setup(enable_validation(TestObject), enable_validation(TestObject))
def test_schema_disable_validation():
    test = TestObject()
    schema_validate_switch(test).disable()
    test.name = 123
    assert test.name == 123


#----------------------------------------------------------------------
@raises(StringTooLongError)
def test_schema_name_too_long():
    test = TestObject()
    test.name = 'abc' * 20


#----------------------------------------------------------------------
def test_schema_nillable():
    test = TestObject()
    test.description = None


#----------------------------------------------------------------------
@raises(NillableFieldInvalidError)
def test_schema_nillable_type_invalid():
    test = TestObject()
    test.description = 123


#----------------------------------------------------------------------
@raises(NillableFieldInvalidError)
def test_schema_nillable_value_too_short():
    test = TestObject()
    test.description = ''


#----------------------------------------------------------------------
def test_schema_validate_all_success():
    test = NoSchemaObject()
    test.name = 'abc'
    test.description = 'def'
    TestSchema().validate(test)
