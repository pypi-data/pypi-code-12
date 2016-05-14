# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

from mock import Mock, patch

from rattail.db import model
from rattail.db.util import QuerySequence
from rattail.importing import importers
from rattail.tests import NullProgress, RattailTestCase
from rattail.tests.importing import ImporterTester


class TestImporter(TestCase):

    def test_init(self):
        importer = importers.Importer()
        self.assertIsNone(importer.model_class)
        self.assertIsNone(importer.model_name)
        self.assertIsNone(importer.key)
        self.assertEqual(importer.fields, [])
        self.assertIsNone(importer.host_system_title)

        # key must be included among the fields
        self.assertRaises(ValueError, importers.Importer, key='upc', fields=[])
        importer = importers.Importer(key='upc', fields=['upc'])
        self.assertEqual(importer.key, ('upc',))
        self.assertEqual(importer.fields, ['upc'])

        # extra bits are passed as-is
        importer = importers.Importer()
        self.assertFalse(hasattr(importer, 'extra_bit'))
        extra_bit = object()
        importer = importers.Importer(extra_bit=extra_bit)
        self.assertIs(importer.extra_bit, extra_bit)

    def test_get_host_objects(self):
        importer = importers.Importer()
        objects = importer.get_host_objects()
        self.assertEqual(objects, [])

    def test_cache_local_data(self):
        importer = importers.Importer()
        self.assertRaises(NotImplementedError, importer.cache_local_data)

    def test_get_local_object(self):
        importer = importers.Importer()
        self.assertFalse(importer.caches_local_data)
        self.assertRaises(NotImplementedError, importer.get_local_object, None)

        someobj = object()
        with patch.object(importer, 'get_single_local_object', Mock(return_value=someobj)):
            obj = importer.get_local_object('somekey')
        self.assertIs(obj, someobj)

        importer.caches_local_data = True
        importer.cached_local_data = {'somekey': {'object': someobj, 'data': {}}}
        obj = importer.get_local_object('somekey')
        self.assertIs(obj, someobj)

    def test_get_single_local_object(self):
        importer = importers.Importer()
        self.assertRaises(NotImplementedError, importer.get_single_local_object, None)

    def test_get_cache_key(self):
        importer = importers.Importer(key='upc', fields=['upc'])
        obj = {'upc': '00074305001321'}
        normal = {'data': obj}
        key = importer.get_cache_key(obj, normal)
        self.assertEqual(key, ('00074305001321',))

    def test_normalize_cache_object(self):
        importer = importers.Importer()
        obj = {'upc': '00074305001321'}
        with patch.object(importer, 'normalize_local_object', new=lambda obj: obj):
            cached = importer.normalize_cache_object(obj)
        self.assertEqual(cached, {'object': obj, 'data': obj})

    def test_normalize_local_object(self):
        importer = importers.Importer(key='upc', fields=['upc', 'description'])
        importer.simple_fields = importer.fields
        obj = Mock(upc='00074305001321', description="Apple Cider Vinegar")
        data = importer.normalize_local_object(obj)
        self.assertEqual(data, {'upc': '00074305001321', 'description': "Apple Cider Vinegar"})

    def test_update_object(self):
        importer = importers.Importer(key='upc', fields=['upc', 'description'])
        importer.simple_fields = importer.fields
        obj = Mock(upc='00074305001321', description="Apple Cider Vinegar")

        newobj = importer.update_object(obj, {'upc': '00074305001321', 'description': "Apple Cider Vinegar"})
        self.assertIs(newobj, obj)
        self.assertEqual(obj.description, "Apple Cider Vinegar")

        newobj = importer.update_object(obj, {'upc': '00074305001321', 'description': "Apple Cider Vinegar 32oz"})
        self.assertIs(newobj, obj)
        self.assertEqual(obj.description, "Apple Cider Vinegar 32oz")

    def test_normalize_host_data(self):
        importer = importers.Importer(key='upc', fields=['upc', 'description'],
                                          progress=NullProgress)

        data = [
            {'upc': '00074305001161', 'description': "Apple Cider Vinegar 16oz"},
            {'upc': '00074305001321', 'description': "Apple Cider Vinegar 32oz"},
        ]

        host_data = importer.normalize_host_data(host_objects=[])
        self.assertEqual(host_data, [])

        host_data = importer.normalize_host_data(host_objects=data)
        self.assertEqual(host_data, data)

        with patch.object(importer, 'get_host_objects', new=Mock(return_value=data)):
            host_data = importer.normalize_host_data()
        self.assertEqual(host_data, data)

    def test_get_deletion_keys(self):
        importer = importers.Importer()
        self.assertFalse(importer.caches_local_data)
        keys = importer.get_deletion_keys()
        self.assertEqual(keys, set())

        importer.caches_local_data = True
        self.assertIsNone(importer.cached_local_data)
        keys = importer.get_deletion_keys()
        self.assertEqual(keys, set())

        importer.cached_local_data = {'delete-me': object()}
        keys = importer.get_deletion_keys()
        self.assertEqual(keys, set(['delete-me']))


class TestFromQuery(RattailTestCase):

    def test_query(self):
        importer = importers.FromQuery()
        self.assertRaises(NotImplementedError, importer.query)

    def test_get_host_objects(self):
        query = self.session.query(model.Product)
        importer = importers.FromQuery()
        with patch.object(importer, 'query', Mock(return_value=query)):
            objects = importer.get_host_objects()
        self.assertIsInstance(objects, QuerySequence)


######################################################################
# fake importer class, tested mostly for basic coverage
######################################################################

class Product(object):
    upc = None
    description = None


class MockImporter(importers.Importer):
    model_class = Product
    key = 'upc'
    simple_fields = ['upc', 'description']
    supported_fields = simple_fields
    caches_local_data = True
    flush_every_x = 1
    session = Mock()

    def normalize_local_object(self, obj):
        return obj

    def update_object(self, obj, host_data, local_data=None):
        return host_data


class TestMockImporter(ImporterTester, TestCase):
    importer_class = MockImporter

    sample_data = {
        '16oz': {'upc': '00074305001161', 'description': "Apple Cider Vinegar 16oz"},
        '32oz': {'upc': '00074305001321', 'description': "Apple Cider Vinegar 32oz"},
        '1gal': {'upc': '00074305011283', 'description': "Apple Cider Vinegar 1gal"},
    }

    def setUp(self):
        self.importer = self.make_importer()

    def test_create(self):
        local = self.copy_data()
        del local['32oz']
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data()
        self.assert_import_created('32oz')
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_create_empty(self):
        with self.host_data({}):
            with self.local_data({}):
                self.import_data()
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_update(self):
        local = self.copy_data()
        local['16oz']['description'] = "wrong description"
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data()
        self.assert_import_created()
        self.assert_import_updated('16oz')
        self.assert_import_deleted()

    def test_delete(self):
        local = self.copy_data()
        local['bogus'] = {'upc': '00000000000000', 'description': "Delete Me"}
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data()
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted('bogus')

    def test_duplicate(self):
        host = self.copy_data()
        host['32oz-dupe'] = host['32oz']
        with self.host_data(host):
            with self.local_data(self.sample_data):
                self.import_data()
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_max_create(self):
        local = self.copy_data()
        del local['16oz']
        del local['1gal']
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(max_create=1)
        self.assert_import_created('16oz')
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_max_total_create(self):
        local = self.copy_data()
        del local['16oz']
        del local['1gal']
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(max_total=1)
        self.assert_import_created('16oz')
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_max_update(self):
        local = self.copy_data()
        local['16oz']['description'] = "wrong"
        local['1gal']['description'] = "wrong"
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(max_update=1)
        self.assert_import_created()
        self.assert_import_updated('16oz')
        self.assert_import_deleted()

    def test_max_total_update(self):
        local = self.copy_data()
        local['16oz']['description'] = "wrong"
        local['1gal']['description'] = "wrong"
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(max_total=1)
        self.assert_import_created()
        self.assert_import_updated('16oz')
        self.assert_import_deleted()

    def test_max_delete(self):
        local = self.copy_data()
        local['bogus1'] = {'upc': '00000000000001', 'description': "Delete Me"}
        local['bogus2'] = {'upc': '00000000000002', 'description': "Delete Me"}
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(max_delete=1)
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted('bogus1')

    def test_max_total_delete(self):
        local = self.copy_data()
        local['bogus1'] = {'upc': '00000000000001', 'description': "Delete Me"}
        local['bogus2'] = {'upc': '00000000000002', 'description': "Delete Me"}
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(max_total=1)
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted('bogus1')
