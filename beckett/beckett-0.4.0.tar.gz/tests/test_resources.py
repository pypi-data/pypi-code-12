#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_resources
----------------------------------

Tests for `beckett.resources` module.
"""

from beckett.resources import BaseResource

from tests.fixtures import PeopleResource


def test_base_resource_attributes():
    """
    Base class tests
    """

    model = BaseResource(id='1')
    assert model.__str__() == '<Resource | 1>'


def test_custom_resource():
    """
    Test our own custom resource - MyTestResource
    """
    data = {
        'name': 'Wort wort',
        'slug': 'sluggy',
        'not_valid': 'nooo'
    }
    instance = PeopleResource(**data)
    # We should have this attribute
    assert hasattr(instance, 'name')
    # But this one is missing
    assert not hasattr(instance, 'another_thing')
    # and this one is not valid
    assert not hasattr(instance, 'not_valid')
    assert instance.__str__() == '<People | Wort wort>'
    # It should also have parent Meta attributes
    assert hasattr(instance.Meta, 'acceptable_status_codes')
