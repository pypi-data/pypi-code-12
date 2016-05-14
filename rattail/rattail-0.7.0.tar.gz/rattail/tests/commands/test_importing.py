# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import argparse
from unittest import TestCase

from mock import Mock, patch

from rattail.core import Object
from rattail.commands import importing
from rattail.importing import ImportHandler
from rattail.importing.rattail import FromRattailToRattail
from rattail.config import RattailConfig
from rattail.tests.importing import ImporterTester
from rattail.tests.importing.test_handlers import MockImportHandler
from rattail.tests.importing.test_importers import MockImporter
from rattail.tests.importing.test_rattail import DualRattailTestCase


class MockImport(importing.ImportSubcommand):

    def get_handler_factory(self):
        return MockImportHandler


class TestImportSubcommandBasics(TestCase):

    # TODO: lame, here only for coverage
    def test_parent_name(self):
        parent = Object(name='milo')
        command = importing.ImportSubcommand(parent=parent)
        self.assertEqual(command.parent_name, 'milo')

    def test_get_handler_factory(self):
        command = importing.ImportSubcommand()
        self.assertRaises(NotImplementedError, command.get_handler_factory)

    def test_get_handler(self):

        # no config
        command = MockImport()
        handler = command.get_handler()
        self.assertIs(type(handler), MockImportHandler)
        self.assertIsNone(handler.config)

        # with config
        config = RattailConfig()
        command = MockImport(config=config)
        handler = command.get_handler()
        self.assertIs(type(handler), MockImportHandler)
        self.assertIs(handler.config, config)

        # dry run
        command = MockImport()
        handler = command.get_handler()
        self.assertFalse(handler.dry_run)
        handler = command.get_handler(dry_run=True)
        self.assertTrue(handler.dry_run)
        args = argparse.Namespace(dry_run=True)
        handler = command.get_handler(args=args)
        self.assertTrue(handler.dry_run)

    def test_add_parser_args(self):
        # TODO: this doesn't really test anything, but does give some coverage..

        # no handler
        command = importing.ImportSubcommand()
        parser = argparse.ArgumentParser()
        command.add_parser_args(parser)

        # with handler
        command = MockImport()
        parser = argparse.ArgumentParser()
        command.add_parser_args(parser)


class TestImportSubcommandRun(ImporterTester, TestCase):

    sample_data = {
        '16oz': {'upc': '00074305001161', 'description': "Apple Cider Vinegar 16oz"},
        '32oz': {'upc': '00074305001321', 'description': "Apple Cider Vinegar 32oz"},
        '1gal': {'upc': '00074305011283', 'description': "Apple Cider Vinegar 1gal"},
    }

    def setUp(self):
        self.command = MockImport()
        self.handler = MockImportHandler()
        self.importer = MockImporter()

    def import_data(self, **kwargs):
        models = kwargs.pop('models', [])
        kwargs.setdefault('dry_run', False)

        kw = {
            'warnings': False,
            'max_create': None,
            'max_update': None,
            'max_delete': None,
            'max_total': None,
            'progress': None,
        }
        kw.update(kwargs)
        args = argparse.Namespace(models=models, **kw)

        # must modify our importer in-place since we need the handler to return
        # that specific instance, below (because the host/local data context
        # managers reference that instance directly)
        self.importer._setup(**kwargs)
        with patch.object(self.command, 'get_handler', Mock(return_value=self.handler)):
            with patch.object(self.handler, 'get_importer', Mock(return_value=self.importer)):
                self.command.run(args)

        if self.handler._result:
            self.result = self.handler._result['Product']
        else:
            self.result = [], [], []

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


class TestImportRattail(DualRattailTestCase):

    def make_command(self, **kwargs):
        kwargs.setdefault('config', self.config)
        return importing.ImportRattail(**kwargs)

    def test_get_handler_factory(self):

        # default handler
        config = RattailConfig()
        command = self.make_command(config=config)
        Handler = command.get_handler_factory()
        self.assertIs(Handler, FromRattailToRattail)

    def test_get_handler_kwargs(self):
        command = self.make_command()
        kwargs = command.get_handler_kwargs()
        self.assertEqual(kwargs, {})

        args = argparse.Namespace(dbkey='other')
        kwargs = command.get_handler_kwargs(args=args)
        self.assertEqual(len(kwargs), 2)
        self.assertIs(kwargs['args'], args)
        self.assertEqual(kwargs['dbkey'], 'other')
