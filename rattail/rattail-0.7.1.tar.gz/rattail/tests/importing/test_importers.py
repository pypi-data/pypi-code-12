# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

from mock import Mock, patch, call

from rattail.db import model
from rattail.db.util import QuerySequence
from rattail.importing import importers
from rattail.tests import NullProgress, RattailTestCase
from rattail.tests.importing import ImporterTester


class ImporterBattery(ImporterTester):
    """
    Battery of tests which can hopefully be ran for any non-bulk importer.
    """

    def test_import_data_empty(self):
        importer = self.make_importer()
        result = importer.import_data()
        self.assertEqual(result, {})

    def test_import_data_dry_run(self):
        importer = self.make_importer()
        self.assertFalse(importer.dry_run)
        importer.import_data(dry_run=True)
        self.assertTrue(importer.dry_run)

    def test_import_data_create(self):
        importer = self.make_importer()
        with patch.object(importer, 'get_key', lambda k: k):
            with patch.object(importer, 'create_object') as create:
                importer.import_data(host_data=[1, 2, 3])
                self.assertEqual(create.call_args_list, [
                    call(1, 1), call(2, 2), call(3, 3)])

    def test_import_data_max_create(self):
        importer = self.make_importer()
        with patch.object(importer, 'get_key', lambda k: k):
            with patch.object(importer, 'create_object') as create:
                importer.import_data(host_data=[1, 2, 3], max_create=1)
                self.assertEqual(create.call_args_list, [call(1, 1)])


class BulkImporterBattery(ImporterBattery):
    """
    Battery of tests which can hopefully be ran for any bulk importer.
    """

    def test_import_data_empty(self):
        importer = self.make_importer()
        result = importer.import_data()
        self.assertEqual(result, 0)


class TestImporter(TestCase):

    def test_init(self):

        # defaults
        importer = importers.Importer()
        self.assertIsNone(importer.model_class)
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

    def test_delete_flag(self):
        # disabled by default
        importer = importers.Importer()
        self.assertTrue(importer.allow_delete)
        self.assertFalse(importer.delete)
        importer.import_data(host_data=[])
        self.assertFalse(importer.delete)

        # but can be enabled
        importer = importers.Importer(delete=True)
        self.assertTrue(importer.allow_delete)
        self.assertTrue(importer.delete)
        importer = importers.Importer()
        self.assertFalse(importer.delete)
        importer.import_data(host_data=[], delete=True)
        self.assertTrue(importer.delete)

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

    def test_model_name_attr(self):
        # default is None
        importer = importers.Importer()
        self.assertIsNone(importer.model_name)

        # but may be overridden via init kwarg
        importer = importers.Importer(model_name='Foo')
        self.assertEqual(importer.model_name, 'Foo')

        # or may inherit its value from 'model_class'
        class Foo:
            pass
        importer = importers.Importer(model_class=Foo)
        self.assertEqual(importer.model_name, 'Foo')

    def test_batch_size_attr(self):
        # default is 200
        importer = importers.Importer()
        self.assertEqual(importer.batch_size, 200)

        # but may be overridden via init kwarg
        importer = importers.Importer(batch_size=0)
        self.assertEqual(importer.batch_size, 0)
        importer = importers.Importer(batch_size=42)
        self.assertEqual(importer.batch_size, 42)

        # batch size determines how often flush occurs
        data = [{'id': i} for i in range(1, 101)]
        importer = importers.Importer(model_name='Foo', key='id', fields=['id'], empty_local_data=True)
        with patch.object(importer, 'create_object'): # just mock that out
            with patch.object(importer, 'flush_create_update') as flush:

                # 4 batches @ 33/per
                importer.import_data(host_data=data, batch_size=33)
                self.assertEqual(flush.call_count, 4)
                flush.reset_mock()

                # 3 batches @ 34/per
                importer.import_data(host_data=data, batch_size=34)
                self.assertEqual(flush.call_count, 3)
                flush.reset_mock()

                # 2 batches @ 50/per
                importer.import_data(host_data=data, batch_size=100)
                self.assertEqual(flush.call_count, 2)
                flush.reset_mock()

                # one extra/final flush happens, whenever the total number of
                # changes happens to match the batch size...

                # 1 batch @ 100/per, plus final flush
                importer.import_data(host_data=data, batch_size=100)
                self.assertEqual(flush.call_count, 2)
                flush.reset_mock()

                # 1 batch @ 200/per
                importer.import_data(host_data=data, batch_size=200)
                self.assertEqual(flush.call_count, 1)
                flush.reset_mock()

                # one extra/final flush also happens when batching is disabled

                # 100 "batches" @ 0/per, plus final flush
                importer.import_data(host_data=data, batch_size=0)
                self.assertEqual(flush.call_count, 101)
                flush.reset_mock()


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


class TestBulkImporter(TestCase, BulkImporterBattery):
    importer_class = importers.BulkImporter
        
    def test_batch_size_attr(self):
        # default is 200
        importer = importers.BulkImporter()
        self.assertEqual(importer.batch_size, 200)

        # but may be overridden via init kwarg
        importer = importers.BulkImporter(batch_size=0)
        self.assertEqual(importer.batch_size, 0)
        importer = importers.BulkImporter(batch_size=42)
        self.assertEqual(importer.batch_size, 42)

        # batch size determines how often flush occurs
        data = [{'id': i} for i in range(1, 101)]
        importer = importers.BulkImporter(model_name='Foo', key='id', fields=['id'], empty_local_data=True)
        with patch.object(importer, 'create_object'): # just mock that out
            with patch.object(importer, 'flush_create_update') as flush:

                # 4 batches @ 33/per
                importer.import_data(host_data=data, batch_size=33)
                self.assertEqual(flush.call_count, 4)
                flush.reset_mock()

                # 3 batches @ 34/per
                importer.import_data(host_data=data, batch_size=34)
                self.assertEqual(flush.call_count, 3)
                flush.reset_mock()

                # 2 batches @ 50/per
                importer.import_data(host_data=data, batch_size=100)
                self.assertEqual(flush.call_count, 2)
                flush.reset_mock()

                # one extra/final flush happens, whenever the total number of
                # changes happens to match the batch size...

                # 1 batch @ 100/per, plus final flush
                importer.import_data(host_data=data, batch_size=100)
                self.assertEqual(flush.call_count, 2)
                flush.reset_mock()

                # 1 batch @ 200/per
                importer.import_data(host_data=data, batch_size=200)
                self.assertEqual(flush.call_count, 1)
                flush.reset_mock()

                # one extra/final flush also happens when batching is disabled

                # 100 "batches" @ 0/per, plus final flush
                importer.import_data(host_data=data, batch_size=0)
                self.assertEqual(flush.call_count, 101)
                flush.reset_mock()


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
        self.import_data(local_data=local)
        self.assert_import_created('32oz')
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_create_empty(self):
        self.import_data(host_data={}, local_data={})
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_update(self):
        local = self.copy_data()
        local['16oz']['description'] = "wrong description"
        self.import_data(local_data=local)
        self.assert_import_created()
        self.assert_import_updated('16oz')
        self.assert_import_deleted()

    def test_delete(self):
        local = self.copy_data()
        local['bogus'] = {'upc': '00000000000000', 'description': "Delete Me"}
        self.import_data(local_data=local, delete=True)
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted('bogus')

    def test_duplicate(self):
        host = self.copy_data()
        host['32oz-dupe'] = host['32oz']
        self.import_data(host_data=host)
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_max_create(self):
        local = self.copy_data()
        del local['16oz']
        del local['1gal']
        self.import_data(local_data=local, max_create=1)
        self.assert_import_created('16oz')
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_max_total_create(self):
        local = self.copy_data()
        del local['16oz']
        del local['1gal']
        self.import_data(local_data=local, max_total=1)
        self.assert_import_created('16oz')
        self.assert_import_updated()
        self.assert_import_deleted()

    def test_max_update(self):
        local = self.copy_data()
        local['16oz']['description'] = "wrong"
        local['1gal']['description'] = "wrong"
        self.import_data(local_data=local, max_update=1)
        self.assert_import_created()
        self.assert_import_updated('16oz')
        self.assert_import_deleted()

    def test_max_total_update(self):
        local = self.copy_data()
        local['16oz']['description'] = "wrong"
        local['1gal']['description'] = "wrong"
        self.import_data(local_data=local, max_total=1)
        self.assert_import_created()
        self.assert_import_updated('16oz')
        self.assert_import_deleted()

    def test_max_delete(self):
        local = self.copy_data()
        local['bogus1'] = {'upc': '00000000000001', 'description': "Delete Me"}
        local['bogus2'] = {'upc': '00000000000002', 'description': "Delete Me"}
        self.import_data(local_data=local, delete=True, max_delete=1)
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted('bogus1')

    def test_max_total_delete(self):
        local = self.copy_data()
        local['bogus1'] = {'upc': '00000000000001', 'description': "Delete Me"}
        local['bogus2'] = {'upc': '00000000000002', 'description': "Delete Me"}
        self.import_data(local_data=local, delete=True, max_total=1)
        self.assert_import_created()
        self.assert_import_updated()
        self.assert_import_deleted('bogus1')

    def test_max_total_delete_with_changes(self):
        local = self.copy_data()
        del local['16oz']
        local['32oz']['description'] = "wrong"
        local['1gal']['description'] = "wrong"
        local['bogus1'] = {'upc': '00000000000001', 'description': "Delete Me"}
        local['bogus2'] = {'upc': '00000000000002', 'description': "Delete Me"}
        self.import_data(local_data=local, delete=True, max_total=3)
        self.assert_import_created('16oz')
        self.assert_import_updated('32oz', '1gal')
        self.assert_import_deleted()
