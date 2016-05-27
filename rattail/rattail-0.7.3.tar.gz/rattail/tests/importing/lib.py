# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import copy
from contextlib import contextmanager

from mock import patch

from rattail.tests import NullProgress


class ImporterTester(object):
    """
    Mixin for importer test suites.
    """
    handler_class = None
    importer_class = None
    sample_data = {}

    def make_handler(self, **kwargs):
        if 'config' not in kwargs and hasattr(self, 'config'):
            kwargs['config'] = self.config
        return self.handler_class(**kwargs)

    def make_importer(self, **kwargs):
        if 'config' not in kwargs and hasattr(self, 'config'):
            kwargs['config'] = self.config
        kwargs.setdefault('progress', NullProgress)
        return self.importer_class(**kwargs)

    def copy_data(self):
        return copy.deepcopy(self.sample_data)

    @contextmanager
    def host_data(self, data):
        self._host_data = data
        host_data = [self.importer.normalize_host_object(obj) for obj in data.itervalues()]
        with patch.object(self.importer, 'normalize_host_data') as normalize:
            normalize.return_value = host_data
            yield

    @contextmanager
    def local_data(self, data):
        self._local_data = data
        local_data = {}
        for key, obj in data.iteritems():
            normal = self.importer.normalize_local_object(obj)
            local_data[self.importer.get_key(normal)] = {'object': obj, 'data': normal}
        with patch.object(self.importer, 'cache_local_data') as cache:
            cache.return_value = local_data
            yield

    def import_data(self, host_data=None, local_data=None, **kwargs):
        if host_data is None:
            host_data = self.sample_data
        if local_data is None:
            local_data = self.sample_data
        with self.host_data(host_data):
            with self.local_data(local_data):
                self.result = self.importer.import_data(**kwargs)

    def assert_import_created(self, *keys):
        created, updated, deleted = self.result
        self.assertEqual(len(created), len(keys))
        for key in keys:
            key = self.importer.get_key(self._host_data[key])
            found = False
            for local_object, host_data in created:
                if self.importer.get_key(host_data) == key:
                    found = True
                    break
            if not found:
                raise self.failureException("Key {} not created when importing with {}".format(key, self.importer))

    def assert_import_updated(self, *keys):
        created, updated, deleted = self.result
        self.assertEqual(len(updated), len(keys))
        for key in keys:
            key = self.importer.get_key(self._host_data[key])
            found = False
            for local_object, local_data, host_data in updated:
                if self.importer.get_key(local_data) == key:
                    found = True
                    break
            if not found:
                raise self.failureException("Key {} not updated when importing with {}".format(key, self.importer))

    def assert_import_deleted(self, *keys):
        created, updated, deleted = self.result
        self.assertEqual(len(deleted), len(keys))
        for key in keys:
            key = self.importer.get_key(self._local_data[key])
            found = False
            for local_object, local_data in deleted:
                if self.importer.get_key(local_data) == key:
                    found = True
                    break
            if not found:
                raise self.failureException("Key {} not deleted when importing with {}".format(key, self.importer))
