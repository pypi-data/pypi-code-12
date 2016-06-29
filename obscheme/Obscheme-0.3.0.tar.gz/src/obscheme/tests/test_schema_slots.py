# -*- coding: utf-8 -*-

from nose.tools import raises

from obscheme.exceptions import WrongTypeError
from obscheme.fields.string import StringField
from obscheme.schema import Schema
from obscheme.schemameta import SchemaMeta


########################################################################
class TestSchema(Schema):

    name = StringField()


########################################################################
class SubTestSchema(TestSchema):

    description = StringField()


########################################################################
class NoSlotsObject(object):
    __metaclass__ = SchemaMeta
    __schema__ = TestSchema()


########################################################################
class SlotsObject(object):
    __metaclass__ = SchemaMeta
    __schema__ = TestSchema()
    __define_slots__ = True


########################################################################
class SlotsSubObject(SlotsObject):
    __schema__ = SubTestSchema()
    __define_slots__ = True


########################################################################
class SubSchemaSlotsObject(SlotsObject):
    __metaclass__ = SchemaMeta
    __schema__ = SubTestSchema()
    __define_slots__ = True


#----------------------------------------------------------------------
def test_schema_no_slots():
    obj = NoSlotsObject()
    assert not hasattr(obj, '__slots__')


#----------------------------------------------------------------------
def test_schema_no_slots_set_attr():
    obj = NoSlotsObject()
    obj.test = 1
    assert obj.test == 1


#----------------------------------------------------------------------
def test_schema_slots():
    obj = SlotsObject()
    assert hasattr(obj, '__slots__')


#----------------------------------------------------------------------
@raises(AttributeError)
def test_schema_slots_set_unknown_attr():
    obj = SlotsObject()
    obj.test = 1


#----------------------------------------------------------------------
def test_schema_subobject_slots():
    obj = SlotsSubObject()
    assert hasattr(obj, '__slots__')


#----------------------------------------------------------------------
def test_schema_subobject_slots_of_both_schemata():
    obj = SlotsSubObject()
    assert hasattr(obj, '__slots__')
    assert 'name' in obj.__slots__
    assert 'description' in obj.__slots__


#----------------------------------------------------------------------
@raises(AttributeError)
def test_schema_subobject_slots_set_unknown_attr():
    obj = SlotsSubObject()
    obj.test = 1


#----------------------------------------------------------------------
def test_schema_subobject_slots_set_known_attr():
    obj = SlotsSubObject()
    obj.name = 'name'
    obj.description = 'description'


#----------------------------------------------------------------------
@raises(WrongTypeError)
def test_schema_subobject_slots_set_known_attr_wrong_type():
    obj = SlotsSubObject()
    obj.name = 'name'
    obj.description = 123


#----------------------------------------------------------------------
def test_schema_subschemaobject_slots():
    obj = SlotsSubObject()
    assert hasattr(obj, '__slots__')


#----------------------------------------------------------------------
def test_schema_subschemaobject_slots_of_both_schemata():
    obj = SlotsSubObject()
    assert hasattr(obj, '__slots__')
    assert 'name' in obj.__slots__
    assert 'description' in obj.__slots__


#----------------------------------------------------------------------
@raises(AttributeError)
def test_schema_subschemaobject_slots_set_unknown_attr():
    obj = SlotsSubObject()
    obj.test = 1


#----------------------------------------------------------------------
def test_schema_subschemaobject_slots_set_known_attr():
    obj = SlotsSubObject()
    obj.name = 'name'
    obj.description = 'description'


#----------------------------------------------------------------------
@raises(WrongTypeError)
def test_schema_subschemaobject_slots_set_known_attr_wrong_type():
    obj = SlotsSubObject()
    obj.name = 'name'
    obj.description = 123
