# -*- coding: utf-8 -*-

from nose.tools import raises

from obscheme.fields.integer import IntegerField, IntegerValueBelowMinError, IntegerValueAboveMaxError

TEST_VALUE = 123
FIELD_NAME = 'test_value'


#----------------------------------------------------------------------
def test_integer_validation_success_simple():
    field = IntegerField()
    field.validate(FIELD_NAME, TEST_VALUE)


#----------------------------------------------------------------------
def test_integer_validation_success_w_min_check():
    field = IntegerField(min_value=3)
    field.validate(FIELD_NAME, TEST_VALUE)


#----------------------------------------------------------------------
def test_integer_validation_success_w_max_check():
    field = IntegerField(max_value=250)
    field.validate(FIELD_NAME, TEST_VALUE)


#----------------------------------------------------------------------
def test_integer_validation_success_w_all_checks():
    field = IntegerField(min_value=3, max_value=250)
    field.validate(FIELD_NAME, TEST_VALUE)


#----------------------------------------------------------------------
@raises(IntegerValueBelowMinError)
def test_integer_validation_too_short():
    field = IntegerField(min_value=150)
    field.validate(FIELD_NAME, TEST_VALUE)


#----------------------------------------------------------------------
@raises(IntegerValueAboveMaxError)
def test_integer_validation_too_long():
    field = IntegerField(max_value=50)
    field.validate(FIELD_NAME, TEST_VALUE)
