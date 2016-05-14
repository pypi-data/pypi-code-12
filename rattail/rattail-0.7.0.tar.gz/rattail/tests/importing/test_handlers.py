# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import unittest

from sqlalchemy import orm
from mock import patch, Mock
from fixture import TempIO

from rattail.db import Session
from rattail.importing import handlers, Importer
from rattail.config import RattailConfig
from rattail.tests import RattailTestCase
from rattail.tests.importing import ImporterTester
from rattail.tests.importing.test_importers import MockImporter
from rattail.tests.importing.test_postgresql import MockBulkImporter


class TestImportHandlerBasics(unittest.TestCase):

    def test_init(self):

        # vanilla
        handler = handlers.ImportHandler()
        self.assertEqual(handler.importers, {})
        self.assertEqual(handler.get_importers(), {})
        self.assertEqual(handler.get_importer_keys(), [])
        self.assertEqual(handler.get_default_keys(), [])

        # with config
        handler = handlers.ImportHandler()
        self.assertIsNone(handler.config)
        config = RattailConfig()
        handler = handlers.ImportHandler(config=config)
        self.assertIs(handler.config, config)

        # dry run
        handler = handlers.ImportHandler()
        self.assertFalse(handler.dry_run)
        handler = handlers.ImportHandler(dry_run=True)
        self.assertTrue(handler.dry_run)

        # extra kwarg
        handler = handlers.ImportHandler()
        self.assertRaises(AttributeError, getattr, handler, 'foo')
        handler = handlers.ImportHandler(foo='bar')
        self.assertEqual(handler.foo, 'bar')

    def test_get_importer(self):
        get_importers = Mock(return_value={'foo': Importer})

        # no importers
        handler = handlers.ImportHandler()
        self.assertIsNone(handler.get_importer('foo'))

        # no config
        with patch.object(handlers.ImportHandler, 'get_importers', get_importers):
            handler = handlers.ImportHandler()
        importer = handler.get_importer('foo')
        self.assertIs(type(importer), Importer)
        self.assertIsNone(importer.config)
        self.assertIs(importer.handler, handler)

        # with config
        config = RattailConfig()
        with patch.object(handlers.ImportHandler, 'get_importers', get_importers):
            handler = handlers.ImportHandler(config=config)
        importer = handler.get_importer('foo')
        self.assertIs(type(importer), Importer)
        self.assertIs(importer.config, config)
        self.assertIs(importer.handler, handler)

        # dry run
        with patch.object(handlers.ImportHandler, 'get_importers', get_importers):
            handler = handlers.ImportHandler()
        importer = handler.get_importer('foo')
        self.assertFalse(importer.dry_run)
        with patch.object(handlers.ImportHandler, 'get_importers', get_importers):
            handler = handlers.ImportHandler(dry_run=True)
        importer = handler.get_importer('foo')
        self.assertTrue(handler.dry_run)

        # host title
        with patch.object(handlers.ImportHandler, 'get_importers', get_importers):
            handler = handlers.ImportHandler()
        importer = handler.get_importer('foo')
        self.assertIsNone(importer.host_system_title)
        handler.host_title = "Foo"
        importer = handler.get_importer('foo')
        self.assertEqual(importer.host_system_title, "Foo")

        # extra kwarg
        with patch.object(handlers.ImportHandler, 'get_importers', get_importers):
            handler = handlers.ImportHandler()
        importer = handler.get_importer('foo')
        self.assertRaises(AttributeError, getattr, importer, 'bar')
        importer = handler.get_importer('foo', bar='baz')
        self.assertEqual(importer.bar, 'baz')

    def test_get_importer_kwargs(self):

        # empty by default
        handler = handlers.ImportHandler()
        self.assertEqual(handler.get_importer_kwargs('foo'), {})

        # extra kwargs are preserved
        handler = handlers.ImportHandler()
        self.assertEqual(handler.get_importer_kwargs('foo', bar='baz'), {'bar': 'baz'})

    def test_begin_transaction(self):
        handler = handlers.ImportHandler()
        with patch.object(handler, 'begin_host_transaction') as begin_host:
            with patch.object(handler, 'begin_local_transaction') as begin_local:
                handler.begin_transaction()
                begin_host.assert_called_once_with()
                begin_local.assert_called_once_with()

    def test_commit_transaction(self):
        handler = handlers.ImportHandler()
        with patch.object(handler, 'commit_host_transaction') as commit_host:
            with patch.object(handler, 'commit_local_transaction') as commit_local:
                handler.commit_transaction()
                commit_host.assert_called_once_with()
                commit_local.assert_called_once_with()

    def test_rollback_transaction(self):
        handler = handlers.ImportHandler()
        with patch.object(handler, 'rollback_host_transaction') as rollback_host:
            with patch.object(handler, 'rollback_local_transaction') as rollback_local:
                handler.rollback_transaction()
                rollback_host.assert_called_once_with()
                rollback_local.assert_called_once_with()


######################################################################
# fake import handler, tested mostly for basic coverage
######################################################################

class MockImportHandler(handlers.ImportHandler):

    def get_importers(self):
        return {'Product': MockImporter}

    def import_data(self, *keys, **kwargs):
        result = super(MockImportHandler, self).import_data(*keys, **kwargs)
        self._result = result
        return result


class TestImportHandlerImportData(ImporterTester, unittest.TestCase):

    sample_data = {
        '16oz': {'upc': '00074305001161', 'description': "Apple Cider Vinegar 16oz"},
        '32oz': {'upc': '00074305001321', 'description': "Apple Cider Vinegar 32oz"},
        '1gal': {'upc': '00074305011283', 'description': "Apple Cider Vinegar 1gal"},
    }

    def setUp(self):
        self.config = RattailConfig()
        self.handler = MockImportHandler(config=self.config)
        self.importer = MockImporter(config=self.config)

    def import_data(self, **kwargs):
        # must modify our importer in-place since we need the handler to return
        # that specific instance, below (because the host/local data context
        # managers reference that instance directly)
        self.importer._setup(**kwargs)
        with patch.object(self.handler, 'get_importer', Mock(return_value=self.importer)):
            result = self.handler.import_data('Product', **kwargs)
        if result:
            self.result = result['Product']
        else:
            self.result = [], [], []

    def test_invalid_importer_key_is_ignored(self):
        handler = handlers.ImportHandler()
        self.assertNotIn('InvalidKey', handler.importers)
        self.assertEqual(handler.import_data('InvalidKey'), {})

    def test_create(self):
        local = self.copy_data()
        del local['32oz']
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data()
        self.assert_import_created('32oz')
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

    def test_dry_run(self):
        local = self.copy_data()
        del local['32oz']
        local['16oz']['description'] = "wrong description"
        local['bogus'] = {'upc': '00000000000000', 'description': "Delete Me"}
        with self.host_data(self.sample_data):
            with self.local_data(local):
                self.import_data(dry_run=True)
        # TODO: maybe need a way to confirm no changes actually made due to dry
        # run; currently results still reflect "proposed" changes.  this rather
        # bogus test is here just for coverage sake
        self.assert_import_created('32oz')
        self.assert_import_updated('16oz')
        self.assert_import_deleted('bogus')

    def test_warnings_run(self):
        local = self.copy_data()
        del local['32oz']
        local['16oz']['description'] = "wrong description"
        local['bogus'] = {'upc': '00000000000000', 'description': "Delete Me"}
        with self.host_data(self.sample_data):
            with self.local_data(local):
                with patch('rattail.importing.handlers.send_email') as send_email:
                    self.assertEqual(send_email.call_count, 0)
                    self.import_data(warnings=True, dry_run=True)
                    self.assertEqual(send_email.call_count, 1)
        # second time is just for more coverage...
        with self.host_data(self.sample_data):
            with self.local_data(local):
                with patch('rattail.importing.handlers.send_email') as send_email:
                    self.handler.command = Mock()
                    self.assertEqual(send_email.call_count, 0)
                    self.import_data(warnings=True)
                    self.assertEqual(send_email.call_count, 1)
        # TODO: maybe need a way to confirm no changes actually made due to dry
        # run; currently results still reflect "proposed" changes.  this rather
        # bogus test is here just for coverage sake
        self.assert_import_created('32oz')
        self.assert_import_updated('16oz')
        self.assert_import_deleted('bogus')


Session = orm.sessionmaker()


class MockFromSQLAlchemyHandler(handlers.FromSQLAlchemyHandler):

    def make_host_session(self):
        return Session()


class MockToSQLAlchemyHandler(handlers.ToSQLAlchemyHandler):

    def make_session(self):
        return Session()


class TestFromSQLAlchemyHandler(unittest.TestCase):

    def test_init(self):
        handler = handlers.FromSQLAlchemyHandler()
        self.assertRaises(NotImplementedError, handler.make_host_session)

    def test_get_importer_kwargs(self):
        session = object()
        handler = handlers.FromSQLAlchemyHandler(host_session=session)
        kwargs = handler.get_importer_kwargs(None)
        self.assertEqual(list(kwargs.iterkeys()), ['host_session'])
        self.assertIs(kwargs['host_session'], session)

    def test_begin_host_transaction(self):
        handler = MockFromSQLAlchemyHandler()
        self.assertIsNone(handler.host_session)
        handler.begin_host_transaction()
        self.assertIsInstance(handler.host_session, orm.Session)
        handler.host_session.close()

    def test_commit_host_transaction(self):
        # TODO: test actual commit for data changes
        session = Session()
        handler = handlers.FromSQLAlchemyHandler(host_session=session)
        self.assertIs(handler.host_session, session)
        handler.commit_host_transaction()
        self.assertIsNone(handler.host_session)

    def test_rollback_host_transaction(self):
        # TODO: test actual rollback for data changes
        session = Session()
        handler = handlers.FromSQLAlchemyHandler(host_session=session)
        self.assertIs(handler.host_session, session)
        handler.rollback_host_transaction()
        self.assertIsNone(handler.host_session)


class TestToSQLAlchemyHandler(unittest.TestCase):

    def test_init(self):
        handler = handlers.ToSQLAlchemyHandler()
        self.assertRaises(NotImplementedError, handler.make_session)

    def test_get_importer_kwargs(self):
        session = object()
        handler = handlers.ToSQLAlchemyHandler(session=session)
        kwargs = handler.get_importer_kwargs(None)
        self.assertEqual(list(kwargs.iterkeys()), ['session'])
        self.assertIs(kwargs['session'], session)

    def test_begin_local_transaction(self):
        handler = MockToSQLAlchemyHandler()
        self.assertIsNone(handler.session)
        handler.begin_local_transaction()
        self.assertIsInstance(handler.session, orm.Session)
        handler.session.close()

    def test_commit_local_transaction(self):
        # TODO: test actual commit for data changes
        session = Session()
        handler = handlers.ToSQLAlchemyHandler(session=session)
        self.assertIs(handler.session, session)
        with patch.object(handler, 'session') as session:
            handler.commit_local_transaction()
            session.commit.assert_called_once_with()
            self.assertFalse(session.rollback.called)
        # self.assertIsNone(handler.session)

    def test_rollback_local_transaction(self):
        # TODO: test actual rollback for data changes
        session = Session()
        handler = handlers.ToSQLAlchemyHandler(session=session)
        self.assertIs(handler.session, session)
        with patch.object(handler, 'session') as session:
            handler.rollback_local_transaction()
            session.rollback.assert_called_once_with()
            self.assertFalse(session.commit.called)
        # self.assertIsNone(handler.session)


######################################################################
# fake bulk import handler, tested mostly for basic coverage
######################################################################

class MockBulkImportHandler(handlers.BulkToPostgreSQLHandler):

    def get_importers(self):
        return {'Department': MockBulkImporter}

    def make_session(self):
        return Session()


class TestBulkImportHandler(RattailTestCase, ImporterTester):

    importer_class = MockBulkImporter

    sample_data = {
        'grocery': {'number': 1, 'name': "Grocery", 'uuid': 'decd909a194011e688093ca9f40bc550'},
        'bulk': {'number': 2, 'name': "Bulk", 'uuid': 'e633d54c194011e687e33ca9f40bc550'},
        'hba': {'number': 3, 'name': "HBA", 'uuid': 'e2bad79e194011e6a4783ca9f40bc550'},
    }

    def setUp(self):
        self.setup_rattail()
        self.tempio = TempIO()
        self.config.set('rattail', 'workdir', self.tempio.realpath())
        self.handler = MockBulkImportHandler(config=self.config)

    def tearDown(self):
        self.teardown_rattail()
        self.tempio = None

    def import_data(self, host_data=None, **kwargs):
        if host_data is None:
            host_data = list(self.copy_data().itervalues())
        with patch.object(self.importer_class, 'normalize_host_data', Mock(return_value=host_data)):
            with patch.object(self.handler, 'make_session', Mock(return_value=self.session)):
                return self.handler.import_data('Department', **kwargs)

    def test_invalid_importer_key_is_ignored(self):
        handler = MockBulkImportHandler()
        self.assertNotIn('InvalidKey', handler.importers)
        self.assertEqual(handler.import_data('InvalidKey'), {})

    def assert_import_created(self, *keys):
        pass

    def assert_import_updated(self, *keys):
        pass

    def assert_import_deleted(self, *keys):
        pass

    def test_normal_run(self):
        if self.postgresql():
            self.import_data()

    def test_dry_run(self):
        if self.postgresql():
            self.import_data(dry_run=True)
