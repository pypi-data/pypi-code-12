# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from disinfect import Field
from disinfect import Mapping
from disinfect import MultiValueError
from disinfect import MappedValueError
from disinfect import Test
from disinfect import tests as t
from disinfect import validate
from pandora.compat import text_type
from pytest import raises


class TestDisinfect(object):
    def test_basics(self):
        test = Test([
            lambda v: text_type(v),
            validate(lambda v: len(v) >= 1, error='Not long enough.'),
            validate(lambda v: len(v) <= 10, error='Too long.'),
        ])

        assert test('Nils') == u'Nils'

        with raises(ValueError) as exc:
            test('')

        assert str(exc.value) == 'Not long enough.'

    def test_wrong_mode(self):
        with raises(RuntimeError) as exc:
            test = Test([], 'wrong')
            test.run(None)

        assert str(exc.value) == 'Invalid mode supplied.'

    def test_mapping(self):
        def String(min_len=1, max_len=150):
            return Test([
                lambda v: text_type(v),
                validate(lambda v: len(v) >= min_len,
                         error='Not long enough.'),
                validate(lambda v: len(v) <= max_len,
                         error='Too long.'),
            ])

        mapping = Mapping({
            'first': String(),
            Field('infix', default=''): String(min_len=0, max_len=40),
            'last': String(),
        })

        user = mapping({
            'first': 'Nils',
            'last': 'Corver',
        })

        assert user == {
            'first': 'Nils',
            'infix': '',
            'last': 'Corver',
        }

        with raises(MappedValueError) as exc:
            mapping({})

        assert exc.value.errors == {
            'first': 'Field is required.',
            'last': 'Field is required.',
        }

    def test_complex(self):
        mapping = Mapping({
            'first': t.String(),
            Field('infix', default=''): t.String(min_len=0,
                                                 max_len=40),
            'last': t.String(),

            'addresses': t.ListOf(Mapping({
                'zipcode': t.String(min_len=5, max_len=5),
                'housenumber': t.Int(min_value=1),
            }))
        })

        user = mapping({
            'first': 'Nils',
            'infix': '',
            'last': 'Corver',
            'addresses': [
                {'zipcode': '71486', 'housenumber': '49'},
                {'zipcode': '59546', 'housenumber': '709'},
            ]
        })

        assert user == {
            'first': 'Nils',
            'infix': '',
            'last': 'Corver',
            'addresses': [
                {'zipcode': '71486', 'housenumber': 49},
                {'zipcode': '59546', 'housenumber': 709},
            ]
        }

        with raises(MultiValueError) as exc:
            mapping({})

        assert exc.value.to_dict() == {
            'first': 'Field is required.',
            'last': 'Field is required.',
            'addresses': 'Field is required.',
        }

        with raises(MultiValueError) as exc:
            mapping({
                'addresses': [
                    {'ignored': 'blah'}
                ]
            })

        assert exc.value.to_dict() == {
            'first': 'Field is required.',
            'last': 'Field is required.',
            'addresses': [{
                'zipcode': 'Field is required.',
                'housenumber': 'Field is required.',
            }]
        }

        with raises(MultiValueError) as exc:
            mapping({
                'addresses': [
                    {'zipcode': '71486', 'housenumber': 49},
                    {'zipcode': '123', 'housenumber': 'abc'},
                    {'zipcode': '59546', 'housenumber': 709},
                ]
            })

        assert exc.value.to_dict() == {
            'first': 'Field is required.',
            'last': 'Field is required.',
            'addresses': [
                None,
                {
                    'zipcode': 'Too short.',
                    'housenumber': 'Not an integer.',
                },
                None
            ]
        }
