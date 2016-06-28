# -*- coding: utf-8 -*-

from nose.tools import raises

from obscheme.fields.list import ListField, ListFieldInvalidError
from obscheme.fields.string import StringField


TEST_LIST_EMPTY = []
TEST_LIST_STRINGS = ['foo', 'bar', 'foobar']
TEST_LIST_MIXED = ['foo', 456, 'foobar']
FIELD_NAME = 'test_value'


#----------------------------------------------------------------------
def test_list_validation_success_empty():
    field = ListField(StringField())
    field.validate(FIELD_NAME, TEST_LIST_EMPTY)


#----------------------------------------------------------------------
def test_list_validation_success():
    field = ListField(StringField())
    field.validate(FIELD_NAME, TEST_LIST_STRINGS)


#----------------------------------------------------------------------
@raises(ListFieldInvalidError)
def test_list_validation_error_type():
    field = ListField(StringField())
    field.validate(FIELD_NAME, TEST_LIST_MIXED)


#----------------------------------------------------------------------
def test_list_validation_index_on_exception():
    field = ListField(StringField())
    try:
        field.validate(FIELD_NAME, TEST_LIST_MIXED)
    except ListFieldInvalidError as e:
        assert e.index == 1
