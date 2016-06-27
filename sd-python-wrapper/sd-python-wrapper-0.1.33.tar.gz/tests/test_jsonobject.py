#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from serverdensity.wrapper import JsonObject
from serverdensity.wrapper import ApiClient


class JsonObjectTest(unittest.TestCase):

    def setUp(self):
        self.schema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'title': 'Test schema',
            'type': 'object',
            'properties': {
                '_id': {
                    'type': 'string',
                    'format': 'mongoId'
                },
                'name': {
                    'type': 'string'
                }
            },
            'required': ['_id']
        }

        self.dummyschema = {
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {}
        }

        self.TestObj = JsonObject
        self.TestObj._schemaobj = self.schema
        self.client = ApiClient('aeou')

    def tearDown(self):
        self.TestObj._schemaobj = None

    def test_instantiate_empty_jsonobject(self):
        obj = self.TestObj()
        self.assertEqual(isinstance(obj, JsonObject), True)

    def test_set_a_simple_attribute(self):
        self.TestObj._schemaobj = self.dummyschema
        obj = self.TestObj()
        obj.key = 'value'
        self.assertEqual(obj.key, 'value')

    def test_raises_attribute_error_when_required_property(self):
        obj = self.TestObj()
        with self.assertRaises(AttributeError):
            obj.key = 'value'

        with self.assertRaisesRegexp(AttributeError, '_id'):
            obj.key = 'value'

    def test_raises_attribute_error_missing_id_with_args(self):
        with self.assertRaises(AttributeError):
            self.TestObj({'key': 'value', 'key2': 'value2'})

    def test_raises_attribute_error_missing_id_with_kwargs(self):
        with self.assertRaises(AttributeError):
            self.TestObj(key='value', key2='value2')

    def test_raises_attribute_error_id_is_not_mongoid(self):
        with self.assertRaises(AttributeError):
            self.TestObj(_id='test')

        with self.assertRaises(AttributeError):
            self.TestObj(_id=123)

        with self.assertRaises(AttributeError):
            # 24 chars, but not mongoId
            self.TestObj(_id='ss1212121212121212121212')

        with self.assertRaisesRegexp(AttributeError, 'mongoId'):
            self.TestObj(_id='test')

    def test_attach_mongoid_successfully(self):
        obj = self.TestObj(_id='4af9f23d8ead0e1d32000000')
        self.assertEqual(obj._id, '4af9f23d8ead0e1d32000000')

    def test_cant_have_certain_protected_values(self):
        self.TestObj._schemaobj = self.dummyschema
        obj = self.TestObj()
        for value in JsonObject._protected:
            with self.assertRaises(AttributeError):
                setattr(obj, value, 'test')

    def test_set_schemaobj_fetches_json_originating_from_file(self):
        self.TestObj._schemaobj = None
        self.TestObj._schemapath = '/schema/testschema.json'
        obj = self.TestObj(key='value')
        self.assertEqual(self.dummyschema, obj._schemaobj)

    def test_initiate_with_apiclient(self):
        self.TestObj._schemaobj = self.dummyschema
        obj = self.TestObj(self.client, {'key': 'value'})
        self.assertEqual(obj.key, 'value')
        self.assertEqual(isinstance(obj.api, ApiClient), True)

    def test_setting_a_token_instantiates_an_apiclient(self):
        obj = self.TestObj('b97da80a41c4f61bff05975ee51eb1aa')
        self.assertEqual(isinstance(obj.api, ApiClient), True)

    def test_set_random_private_property_without_validation_check(self):
        obj = self.TestObj()
        obj._random = 'random data'
        self.assertEqual(obj._random, 'random data')

    def test_raise_attribute_error_if_api_is_none(self):
        obj = self.TestObj()
        with self.assertRaises(TypeError):
            obj.api.create()


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
