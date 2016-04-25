# -*- encoding: utf-8 -*-
import unittest
from any2 import recursive_getattr
from any2csv.main import CSVAddon


class Foo(object):
    def __init__(self, value):
        self.field1 = 'foo1_%s' % value
        self.field2 = 'foo1_%s' % value
        self.unicodefield = u'Jérôme'


class TestGetattr(unittest.TestCase):

    def setUp(self):
        self.foo = Foo("X")

    def test_recursive_default_nodot(self):

        # if we try to get a value which is not present on our obj
        # and has no dot in its representation we should get the default
        res = recursive_getattr(self.foo, "fieldZ", default_value="Nope")
        assert res == "Nope"

    def test_recursive_default_dot(self):

        # if we try to get a value which is not present on our obj
        # and has no dot in its representation we should get the default
        res = recursive_getattr(self.foo, "field.Z", default_value="ZNope")
        assert res == "ZNope"


class TestCSVAddon(unittest.TestCase):
    def setUp(self):
        column_mappings = [
            {'attr': 'field1', 'colname': 'field 1'},
            {'attr': 'field2', 'colname': 'field 2'},
            {'attr': 'unicodefield', 'colname': 'Unicode Field'},
            {'attr': 'another', 'colname': 'Another'},
        ]
        self.foo = CSVAddon(Foo("X"), column_mappings=column_mappings)

    def test_encodedval(self):
        res1 = self.foo.get('Unicode Field', default_value=None)
        assert res1 == u'Jérôme'
