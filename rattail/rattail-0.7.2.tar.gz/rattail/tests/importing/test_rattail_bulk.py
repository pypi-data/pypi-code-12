# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from mock import patch, Mock
from fixture import TempIO

from rattail.importing import rattail_bulk as bulk
from rattail.tests.importing import ImporterTester
from rattail.tests.importing.test_rattail import DualRattailTestCase


class BulkImportTester(DualRattailTestCase, ImporterTester):

    handler_class = bulk.BulkFromRattailToRattail

    def setUp(self):
        self.setup_rattail()
        self.tempio = TempIO()
        self.config.set('rattail', 'workdir', self.tempio.realpath())
        self.handler = self.make_handler()

        # TODO: no-op for coverage, how lame is that
        self.handler.get_default_keys()

    def tearDown(self):
        self.teardown_rattail()
        self.tempio = None

    @property
    def model_name(self):
        return self.make_importer().model_name

    def get_fields(self):
        return self.make_importer().fields

    def make_handler(self, **kwargs):
        if 'config' not in kwargs and hasattr(self, 'config'):
            kwargs['config'] = self.config
        return self.handler_class(**kwargs)

    def import_data(self, host_data=None, **kwargs):
        if host_data is None:
            fields = self.get_fields()
            host_data = list(self.copy_data().itervalues())
            for data in host_data:
                for field in fields:
                    data.setdefault(field, None)
        with patch.object(self.importer_class, 'normalize_host_data', Mock(return_value=host_data)):
            with patch.object(self.handler, 'make_host_session', Mock(return_value=self.host_session)):
                return self.handler.import_data(self.model_name, **kwargs)


class TestPersonImport(BulkImportTester):

    importer_class = bulk.PersonImporter

    sample_data = {
        'fred': {
            'uuid': 'fred',
            'first_name': 'Fred',
            'last_name': 'Flintstone',
        },
        'maurice': {
            'uuid': 'maurice',
            'first_name': 'Maurice',
            'last_name': 'Jones',
        },
        'zebra': {
            'uuid': 'zebra',
            'first_name': 'Zebra',
            'last_name': 'Jones',
        },
    }

    def test_create(self):
        if self.postgresql():
            result = self.import_data()
            self.assertEqual(result, {'Person': 3})

    def test_max_create(self):
        if self.postgresql():
            result = self.import_data(max_create=1)
            self.assertEqual(result, {'Person': 1})


class TestProductImport(BulkImportTester):

    importer_class = bulk.ProductImporter

    def test_simple_fields(self):
        importer = self.make_importer()
        self.assertNotIn('regular_price_uuid', importer.simple_fields)
        self.assertNotIn('current_price_uuid', importer.simple_fields)
