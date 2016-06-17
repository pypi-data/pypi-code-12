# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import datetime
import unittest

import sqlalchemy as sa
from sqlalchemy import orm
from fixture import TempIO

from rattail.db import Session, model
from rattail.importing import postgresql as pgimport
from rattail.config import RattailConfig
from rattail.exceptions import ConfigurationError
from rattail.tests import RattailTestCase, NullProgress
from rattail.tests.importing import ImporterTester
from rattail.tests.importing.test_rattail import DualRattailTestCase
from rattail.time import localtime


class Widget(object):
    pass


class TestBulkToPostgreSQL(unittest.TestCase):

    def setUp(self):
        self.tempio = TempIO()
        self.config = RattailConfig()
        self.config.set('rattail', 'workdir', self.tempio.realpath())
        self.config.set('rattail', 'timezone.default', 'America/Chicago')

    def tearDown(self):
        self.tempio = None

    def make_importer(self, **kwargs):
        kwargs.setdefault('config', self.config)
        kwargs.setdefault('fields', ['id']) # hack
        return pgimport.BulkToPostgreSQL(**kwargs)

    def test_data_path_property(self):
        self.config.set('rattail', 'workdir', '/tmp')
        importer = pgimport.BulkToPostgreSQL(config=self.config, fields=['id'])

        # path leverages model name, so default is None
        self.assertEqual(importer.data_path, '/tmp/import_bulk_postgresql_None.csv')

        # but it will reflect model name
        importer.model_name = 'Foo'
        self.assertEqual(importer.data_path, '/tmp/import_bulk_postgresql_Foo.csv')

    def test_setup(self):
        importer = self.make_importer()
        self.assertFalse(hasattr(importer, 'data_buffer'))
        importer.setup()
        self.assertIsNotNone(importer.data_buffer)
        importer.data_buffer.close()

    def test_teardown(self):
        importer = self.make_importer()
        importer.data_buffer = open(importer.data_path, 'wb')
        importer.teardown()
        self.assertIsNone(importer.data_buffer)

    def test_prep_value_for_postgres(self):
        importer = self.make_importer()

        # constants
        self.assertEqual(importer.prep_value_for_postgres(None), '\\N')
        self.assertEqual(importer.prep_value_for_postgres(True), 't')
        self.assertEqual(importer.prep_value_for_postgres(False), 'f')

        # datetime (local zone is Chicago/CDT; UTC-5)
        value = localtime(self.config, datetime.datetime(2016, 5, 13, 12))
        self.assertEqual(importer.prep_value_for_postgres(value), '2016-05-13 17:00:00')

        # strings...

        # backslash is escaped by doubling
        self.assertEqual(importer.prep_value_for_postgres('\\'), '\\\\')

        # newlines are collapsed (\r\n -> \n) and escaped
        self.assertEqual(importer.prep_value_for_postgres('one\rtwo\nthree\r\nfour\r\nfive\nsix\rseven'), 'one\\rtwo\\nthree\\r\\nfour\\r\\nfive\\nsix\\rseven')

    def test_prep_data_for_postgres(self):
        importer = self.make_importer()
        time = localtime(self.config, datetime.datetime(2016, 5, 13, 12))
        data = {
            'none': None,
            'true': True,
            'false': False,
            'datetime': time,
            'backslash': '\\',
            'newlines': 'one\rtwo\nthree\r\nfour\r\nfive\nsix\rseven',
        }
        data = importer.prep_data_for_postgres(data)
        self.assertEqual(data['none'], '\\N')
        self.assertEqual(data['true'], 't')
        self.assertEqual(data['false'], 'f')
        self.assertEqual(data['datetime'], '2016-05-13 17:00:00')
        self.assertEqual(data['backslash'], '\\\\')
        self.assertEqual(data['newlines'], 'one\\rtwo\\nthree\\r\\nfour\\r\\nfive\\nsix\\rseven')


######################################################################
# fake importer class, tested mostly for basic coverage
######################################################################

class MockBulkImporter(pgimport.BulkToPostgreSQL):
    model_class = model.Department
    key = 'uuid'

    def normalize_local_object(self, obj):
        return obj

    def update_object(self, obj, host_data, local_data=None):
        return host_data


class TestMockBulkImporter(DualRattailTestCase, ImporterTester):
    importer_class = MockBulkImporter

    sample_data = {
        1: {'number': 1, 'name': "Grocery", 'uuid': 'decd909a194011e688093ca9f40bc550'},
        2: {'number': 2, 'name': "Bulk", 'uuid': 'e633d54c194011e687e33ca9f40bc550'},
        3: {'number': 3, 'name': "HBA", 'uuid': 'e2bad79e194011e6a4783ca9f40bc550'},
    }

    def setUp(self):
        self.setup_rattail()
        self.tempio = TempIO()
        self.config.set('rattail', 'workdir', self.tempio.realpath())
        self.importer = self.make_importer()

    def tearDown(self):
        self.teardown_rattail()
        self.tempio = None

    def make_importer(self, **kwargs):
        kwargs.setdefault('config', self.config)
        return super(TestMockBulkImporter, self).make_importer(**kwargs)

    def import_data(self, **kwargs):
        self.importer.session = self.session
        self.importer.host_session = self.host_session
        self.result = self.importer.import_data(**kwargs)

    def assert_import_created(self, *keys):
        pass

    def assert_import_updated(self, *keys):
        pass

    def assert_import_deleted(self, *keys):
        pass

    def test_create(self):
        if self.postgresql():
            with self.host_data(self.sample_data):
                self.import_data()
            self.assert_import_created(3)

    def test_create_empty(self):
        if self.postgresql():
            with self.host_data({}):
                self.import_data()
            self.assert_import_created(0)

    def test_max_create(self):
        if self.postgresql():
            with self.host_data(self.sample_data):
                with self.local_data({}):
                    self.import_data(max_create=1)
            self.assert_import_created(1)

    def test_max_total_create(self):
        if self.postgresql():
            with self.host_data(self.sample_data):
                with self.local_data({}):
                    self.import_data(max_total=1)
            self.assert_import_created(1)

    # # TODO: a bit hacky, leveraging the fact that 'user' is a reserved word
    # def test_table_name_is_reserved_word(self):
    #     if self.postgresql():
    #         from rattail.importing.rattail_bulk import UserImporter
    #         data = {
    #             '521a788e195911e688c13ca9f40bc550': {
    #                 'uuid': '521a788e195911e688c13ca9f40bc550',
    #                 'username': 'fred',
    #                 'active': True,
    #             },
    #         }
    #         self.importer = UserImporter(config=self.config)
    #         # with self.host_data(data):
    #         self.import_data(host_data=data)
    #         # self.assert_import_created(3)
