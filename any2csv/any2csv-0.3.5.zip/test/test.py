# -*- encoding: utf-8 -*-
import unittest
import codecs
import six
import os
from any2csv import Any2CSV, ColumnMappingError


class TestAny2CSV(unittest.TestCase):

    def setUp(self):
        class Foo(object):
            def __init__(self, value):
                self.field1 = 'foo1_%s' % value
                self.field2 = 'foo1_%s' % value

        class Bar(object):
            def __init__(self, value):
                self.field1 = 'bar1_%s' % value
                self.field2 = 'bar2_%s' % value
                self.foo = Foo(value)

        class Dummy(object):
            def __init__(self, value):
                self.field1 = 'dummy1_%s' % value
                self.field2 = 'dummy2_%s' % value
                self.bar = Bar(value)

        self.foo_list = [Foo('d1'), Foo('d2'), Foo('d3'), Foo('d4')]
        self.bar_list = [Bar('b1'), Bar('b2'), Bar('b3'), Bar('b4')]
        self.dummy_list = [Dummy('r1'), Dummy('r2'), Dummy('r3'), Dummy('r4')]
        self.simple_dicts = [
            {
                'name': u'Florent Aide',
                'city': u'Paris',
                'accented_data': u'Forêt'
            }
        ]

    def tearDown(self):
        try:
            os.unlink('test/test.csv')
        except:
            pass

    def test_instanciation(self):
        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {'attr': 'field1', 'colname': 'field 1'},
                {'attr': 'field2', 'colname': 'field 2'},
            ]
        )

        assert isinstance(any2csv, Any2CSV)

    def test_write_simple_csv(self):

        any2csv = Any2CSV(
            target_filename='test/test.csv',

            column_mappings=[
                {'attr': 'field1', 'colname': 'field 1'},
                {'attr': 'field2', 'colname': 'field 2'},
            ]
        )

        any2csv.write(self.foo_list)

        require = [
            '"foo1_d1";"foo1_d1"\n',
            '"foo1_d2";"foo1_d2"\n',
            '"foo1_d3";"foo1_d3"\n',
            '"foo1_d4";"foo1_d4"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_write_dict_with_unicode(self):
        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {'attr': 'city', 'colname': 'city'},
                {'attr': 'accented_data', 'colname': 'accented_data'},
                {'attr': 'name', 'colname': 'name'},
            ],
            show_first_line=True
        )

        any2csv.write(self.simple_dicts)
        require = [
            u'"city";"accented_data";"name"\n',
            u'"Paris";"Forêt";"Florent Aide"\n',
        ]

        if six.PY2:
            result = codecs.open('test/test.csv', 'rb', 'utf-8').readlines()
        else:
            result = open('test/test.csv').readlines()

        print(require)
        print(result)
        assert require == result

    def test_write_simple_csv_with_header(self):
        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {'attr': 'field1', 'colname': 'field 1'},
                {'attr': 'field2', 'colname': 'field 2'},
            ],
            show_first_line=True
        )

        any2csv.write(self.foo_list)

        require = [
            '"field 1";"field 2"\n',
            '"foo1_d1";"foo1_d1"\n',
            '"foo1_d2";"foo1_d2"\n',
            '"foo1_d3";"foo1_d3"\n',
            '"foo1_d4";"foo1_d4"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_write_simple_csv_with_renderer(self):

        def renderer_field1(value=""):
            return value.split('_')[1]

        def renderer_field2(value=""):
            import decimal
            return '%s%s' % (
                value,
                abs(
                    decimal.Decimal('10.2047842').quantize(
                        decimal.Decimal('0.1')
                    )
                )
            )

        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {
                    'attr': 'field1',
                    'colname': 'field 1',
                    'renderer': renderer_field1,
                },
                {
                    'attr': 'field2',
                    'colname': 'field 2',
                    'renderer': renderer_field2,
                },
            ],
            show_first_line=True
        )

        any2csv.write(self.foo_list)

        require = [
            '"field 1";"field 2"\n',
            '"d1";"foo1_d110.2"\n',
            '"d2";"foo1_d210.2"\n',
            '"d3";"foo1_d310.2"\n',
            '"d4";"foo1_d410.2"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_write_simple_csv_with_sub_object(self):
        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {'attr': 'foo.field1', 'colname': 'field 1'},
                {'attr': 'field2', 'colname': 'field 2'},
            ]
        )

        any2csv.write(self.bar_list)

        require = [
            '"foo1_b1";"bar2_b1"\n',
            '"foo1_b2";"bar2_b2"\n',
            '"foo1_b3";"bar2_b3"\n',
            '"foo1_b4";"bar2_b4"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_write_simple_csv_with_sub_double_level_object(self):
        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {'attr': 'field1', 'colname': 'field1'},
                {'attr': 'bar.field2', 'colname': 'field2'},
                {'attr': 'bar.foo.field1', 'colname': 'field3'},
            ]
        )

        any2csv.write(self.dummy_list)

        require = [
            '"dummy1_r1";"bar2_r1";"foo1_r1"\n',
            '"dummy1_r2";"bar2_r2";"foo1_r2"\n',
            '"dummy1_r3";"bar2_r3";"foo1_r3"\n',
            '"dummy1_r4";"bar2_r4";"foo1_r4"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_complex_1(self):

        any2csv = Any2CSV(
            target_filename='test/test.csv',
            show_first_line=True,
            column_mappings=[
                {'attr': 'field1', 'colname': 'field1'},
                {'colname': 'field2', 'renderer': u'23'},
                {'colname': 'field3', 'attr': 'bar.foo.field1'},
                {'colname': 'field4', 'renderer': u'Hello World !!!'}
            ]
        )
        any2csv.write(self.dummy_list)
        require = [
            '"field1";"field2";"field3";"field4"\n',
            '"dummy1_r1";"23";"foo1_r1";"Hello World !!!"\n',
            '"dummy1_r2";"23";"foo1_r2";"Hello World !!!"\n',
            '"dummy1_r3";"23";"foo1_r3";"Hello World !!!"\n',
            '"dummy1_r4";"23";"foo1_r4";"Hello World !!!"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_complex_2(self):

        def say_hello(value):
            return 'Hello %s' % value

        any2csv = Any2CSV(
            target_filename='test/test.csv',
            column_mappings=[
                {'attr': 'field1', 'colname': 'field1'},
                {'colname': 'field2', 'renderer': u'23'},
                {'colname': 'field3', 'attr': 'bar.foo.field1'},
                {'colname': 'field4', 'renderer': say_hello, 'attr': 'field1'}
            ],
            show_first_line=True
        )
        any2csv.write(self.dummy_list)
        require = [
            '"field1";"field2";"field3";"field4"\n',
            '"dummy1_r1";"23";"foo1_r1";"Hello dummy1_r1"\n',
            '"dummy1_r2";"23";"foo1_r2";"Hello dummy1_r2"\n',
            '"dummy1_r3";"23";"foo1_r3";"Hello dummy1_r3"\n',
            '"dummy1_r4";"23";"foo1_r4";"Hello dummy1_r4"\n',
        ]

        result = open('test/test.csv').readlines()
        print(require)
        print(result)
        assert require == result

    def test_error_1(self):
        error_found = False
        try:
            any2csv = Any2CSV(
                target_filename='test/test.csv',
                show_first_line=True,
                column_mappings=[
                    {'colname': 'field4'}
                ]
            )
            any2csv.write(self.dummy_list)

        except ColumnMappingError as e:
            error_found = True

        assert error_found is True

    def test_error_2(self):
        error_found = False
        try:
            any2csv = Any2CSV(
                target_filename='test/test.csv',
                show_first_line=True,
                column_mappings=[
                    {'renderer': 'field1'}
                ]
            )
            any2csv.write(self.dummy_list)
        except ColumnMappingError as e:
            error_found = True

        assert error_found is True

    def test_error_3(self):
        def foo(param):
            return param

        error_found = False
        try:
            any2csv = Any2CSV(
                target_filename='test/test.csv',
                show_first_line=True,
                column_mappings=[
                    {'colname': 'field1', 'renderer': foo}
                ]
            )
            any2csv.write(self.dummy_list)

        except ColumnMappingError as e:
            error_found = True

        assert error_found is True
