# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from contextlib import contextmanager
from disinfect import tests as t
from poort.utils import FileStorage
from pytest import raises
import datetime as dt
import re


@contextmanager
def raises_message(error_type, message, eq=True):
    with raises(error_type) as exc:
        yield

    if eq:
        assert str(exc.value) == message
    else:
        assert message in str(exc.value)


class TestTests(object):
    def test_string(self):
        test = t.String()
        assert test('Nils') == 'Nils'
        assert test(u'Níls') == u'Níls'
        assert test('<script>test') == 'test'

        test = t.String(min_len=None, max_len=None, strip_html=False)
        assert test('') == ''
        assert test('<script>test') == '<script>test'

    def test_int(self):
        test = t.Int(1, 40)
        assert test('4') == 4

        with raises(ValueError) as exc:
            test('abc')
        assert str(exc.value) == 'Not an integer.'

        with raises(ValueError) as exc:
            test('99')
        assert str(exc.value) == 'Too high.'

        with raises(ValueError) as exc:
            test('-4')
        assert str(exc.value) == 'Too low.'

    def test_float(self):
        test = t.Float(1, 40)
        assert test('4') == 4.0

        with raises(ValueError) as exc:
            test('abc')
        assert str(exc.value) == 'Not a float.'

        with raises(ValueError) as exc:
            test('99.0')
        assert str(exc.value) == 'Too high.'

        with raises(ValueError) as exc:
            test('-4.0')
        assert str(exc.value) == 'Too low.'

        test = t.Float()
        assert test('4') == 4.0

    def test_boolean(self):
        test = t.Boolean()

        assert test('f') is False
        assert test('true') is True

        with raises(ValueError) as exc:
            test('')
        assert str(exc.value) == 'Not a boolean value.'

        test = t.Boolean(true_unless_false=True)

        assert test('f') is False
        assert test('true') is True
        assert test('') is True

        test = t.Boolean(none_values=t.BOOL_FIELD_NONE_VALUES)

        assert test('f') is False
        assert test('true') is True
        assert test('null') is None

        test = t.Boolean(true_values=['ja', 'j'],
                         false_values=['nee', 'n'])

        assert test('ja') is True
        assert test('nee') is False

        with raises(ValueError) as exc:
            test('yes')
        assert str(exc.value) == 'Not a boolean value.'

    def test_enum(self):
        test = t.Enum(['red', 'green', 'blue'])
        assert test('red') == 'red'

        test = t.Enum([1, 2, 3, 4], t.Int())
        assert test('3') == 3

    def test_set(self):
        test = t.Set(['red', 'green', 'blue'])
        assert test('red,blue') == ['red', 'blue']

        test = t.Set([1, 2, 3, 4], t.Int())
        assert test('2,3') == [2, 3]

    def test_list_of(self):
        test = t.ListOf(t.Boolean())
        assert test('yes,yes,no') == [True, True, False]

        with raises(ValueError) as exc:
            test('bluh,blah,no')
        assert exc.value.to_dict() == [
            'Not a boolean value.',
            'Not a boolean value.',
            None,
        ]

        test = t.Set([1, 2, 3, 4], t.Int())
        assert test('2,3') == [2, 3]

    def test_regex(self):
        test = t.Regex(r'[a-z]+')
        assert test('test') == 'test'

        test = t.Regex(re.compile(r'[a-z]+'))
        assert test('test') == 'test'

        with raises(ValueError):
            assert test('123')

    def test_date_time(self):
        now = dt.datetime.now() - dt.timedelta(days=12)

        test = t.DateTime()

        result = test(now.strftime('%Y-%m-%d %H:%M:%S'))
        assert isinstance(result, dt.datetime)
        assert result.toordinal() == now.toordinal()

        result = test(now.strftime('%Y-%m-%d %H:%M'))
        assert result.toordinal() == now.replace(second=0).toordinal()

        with raises(ValueError):
            test('abc')

        should_all_raise = [
            '9999-99-99 99:99',
            '9999-99-99 99:99:99',
            '2000-99-99 99:99:99',
            '2000-01-99 99:99:99',
            '2000-01-01 99:99:99',
            '2000-01-01 01:99:99',
            '2000-01-01 01:01:99',
            '0000-01-01 01:01:01',
        ]
        for value in should_all_raise:
            with raises(ValueError):
                test(value)

        test = t.DateTime(r'[0-9-]+ [0-9:]+',
                          [
                              '%d-%m-%Y %H:%M',
                              '%d-%m-%Y %H:%M:%S',
                          ])

        result = test(now.strftime('%d-%m-%Y %H:%M'))
        assert isinstance(result, dt.datetime)
        assert result.toordinal() == now.replace(second=0).toordinal()

        with raises(ValueError):
            result = test(now.strftime('%Y-%m-%d %H:%M'))

    def test_date(self):
        now = dt.datetime.now() - dt.timedelta(days=12)
        now = now.replace(hour=0, minute=0, second=0)

        test = t.Date()

        result = test(now.strftime('%Y-%m-%d'))
        assert isinstance(result, dt.date)
        assert result.toordinal() == now.toordinal()

        with raises(ValueError):
            test('abc')

        should_all_raise = [
            '9999-99-99',
            '9999-99-99',
            '2000-99-99',
            '2000-01-99',
            '0000-01-01',
        ]
        for value in should_all_raise:
            with raises(ValueError):
                test(value)

        test = t.Date(r'[0-9-]+',
                      [
                          '%d-%m-%Y',
                      ])

        result = test(now.strftime('%d-%m-%Y'))
        assert isinstance(result, dt.date)
        assert result.toordinal() == now.toordinal()

        with raises(ValueError):
            result = test(now.strftime('%Y-%m-%d'))

    def test_date_time_future_and_past(self):
        future = dt.datetime.now() + dt.timedelta(days=12)
        future = future.replace(second=0)

        test = t.DateTime()

        with raises(ValueError):
            test(future.strftime('%Y-%m-%d %H:%M'))

        test = t.DateTime(error_after_today=None)

        result = test(future.strftime('%Y-%m-%d %H:%M'))
        assert isinstance(result, dt.datetime)
        assert result.toordinal() == future.toordinal()

        test = t.DateTime()

        with raises(ValueError):
            test('1870-05-20 14:55')

        test = t.DateTime(error_before_1900=None)

        result = test('1870-05-20 14:55')
        assert isinstance(result, dt.datetime)
        assert list(result.timetuple()[:6]) == [1870, 5, 20, 14, 55, 0]

    def test_email(self):
        test = t.Email()
        assert test('nils@corver.it') == 'nils@corver.it'

        with raises_message(ValueError, 'Missing at in e-mail address.'):
            test('corver.it')

        with raises_message(ValueError, 'Missing dot in e-mail address.'):
            test('nils@')

        with raises_message(ValueError, 'Invalid e-mail address.'):
            test('1@1.^not&valid')

        assert test('nils@this-domain-must-not-exist.nowhere')

        test = t.Email(check_mx=True)
        with raises_message(ValueError, 'Invalid e-mail address.'):
            assert test('nils@this-domain-must-not-exist.nowhere')

    def test_upload(self):
        test = t.Upload()
        file_storage = FileStorage(filename=__file__)

        assert test(file_storage) is file_storage
