# -*- coding: utf-8 -*-

from nose.tools import raises

from obscheme.fields.string import StringField, StringTooShortError, StringTooLongError

TEST_STRING = 'test123'
FIELD_NAME = 'test_value'


#----------------------------------------------------------------------
def test_string_validation_success_simple():
    field = StringField()
    field.validate(FIELD_NAME, TEST_STRING)


#----------------------------------------------------------------------
def test_string_validation_success_w_min_check():
    field = StringField(min_length=3)
    field.validate(FIELD_NAME, TEST_STRING)


#----------------------------------------------------------------------
def test_string_validation_success_w_max_check():
    field = StringField(max_length=12)
    field.validate(FIELD_NAME, TEST_STRING)


#----------------------------------------------------------------------
def test_string_validation_success_w_all_checks():
    field = StringField(min_length=3, max_length=12)
    field.validate(FIELD_NAME, TEST_STRING)


#----------------------------------------------------------------------
@raises(StringTooShortError)
def test_string_validation_too_short():
    field = StringField(min_length=12)
    field.validate(FIELD_NAME, TEST_STRING)


#----------------------------------------------------------------------
@raises(StringTooLongError)
def test_string_validation_too_long():
    field = StringField(max_length=3)
    field.validate(FIELD_NAME, TEST_STRING)
