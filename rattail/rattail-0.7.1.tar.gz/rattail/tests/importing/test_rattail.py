# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

import sqlalchemy as sa
from mock import patch
from fixture import TempIO

from rattail.db import model, Session, SessionBase, auth
from rattail.importing import rattail as rattail_importing
from rattail.tests import RattailMixin, RattailTestCase
from rattail.tests.importing import ImporterTester


class DualRattailMixin(RattailMixin):

    def setup_rattail(self):
        super(DualRattailMixin, self).setup_rattail()

        if 'host' not in self.config.rattail_engines:
            self.config.rattail_engines['host'] = sa.create_engine('sqlite://')

        self.host_engine = self.config.rattail_engines['host']
        self.config.setdefault('rattail.db', 'keys', 'default, host')
        self.config.setdefault('rattail.db', 'host.url', unicode(self.host_engine.url))
        model = self.get_rattail_model()
        model.Base.metadata.create_all(bind=self.host_engine)
        self.host_session = Session(bind=self.host_engine)
        
    def teardown_rattail(self):
        super(DualRattailMixin, self).teardown_rattail()

        self.host_session.close()
        model = self.get_rattail_model()
        model.Base.metadata.drop_all(bind=self.config.rattail_engines['host'])

        if hasattr(self, 'tempio'):
            self.tempio = None


class DualRattailTestCase(DualRattailMixin, TestCase):
    pass


class TestFromRattailHandler(RattailTestCase, ImporterTester):
    handler_class = rattail_importing.FromRattailHandler
        
    def test_make_host_session(self):
        handler = self.make_handler()
        session = handler.make_host_session()
        self.assertIsInstance(session, SessionBase)
        self.assertIs(session.bind, self.config.rattail_engine)


class TestFromRattailToRattail(DualRattailTestCase, ImporterTester):
    handler_class = rattail_importing.FromRattailToRattail

    def test_host_title(self):
        handler = self.make_handler()
        self.assertEqual(handler.host_title, "Rattail (host)")

    # TODO
    def test_default_keys(self):
        handler = self.make_handler()
        handler.get_default_keys()

    def test_make_session(self):
        handler = self.make_handler()
        session = handler.make_session()
        self.assertIsInstance(session, SessionBase)
        self.assertIs(session.bind, self.config.rattail_engine)

    def test_make_host_session(self):

        # default is 'host'
        handler = self.make_handler()
        session = handler.make_host_session()
        self.assertIsInstance(session, SessionBase)
        self.assertIs(session.bind, self.host_engine)

        # invalid dbkey
        handler = self.make_handler(dbkey='other')
        self.assertRaises(KeyError, handler.make_host_session)

        # alternate dbkey
        self.config.rattail_engines['other'] = self.config.rattail_engines['host']
        handler = self.make_handler(dbkey='other')
        session = handler.make_host_session()
        self.assertIsInstance(session, SessionBase)
        self.assertIs(session.bind, self.host_engine)


class TestFromRattail(DualRattailTestCase):

    def make_importer(self, model_class=None, **kwargs):
        kwargs.setdefault('host_session', self.host_session)
        importer = rattail_importing.FromRattail(self.config, **kwargs)
        if model_class:
            importer.model_class = model_class
        return importer

    def test_host_model_class(self):
        importer = self.make_importer()
        self.assertIsNone(importer.model_class)
        self.assertIsNone(importer.host_model_class)
        importer = self.make_importer(model.Product)
        self.assertIs(importer.host_model_class, model.Product)

    def test_query(self):
        importer = self.make_importer(model.Product)
        importer.query()

    def test_normalize_host_object(self):
        importer = self.make_importer(model.Product)
        product = model.Product()
        with patch.object(importer, 'normalize_local_object') as normalize_local:
            normalize_local.return_value = {}
            data = importer.normalize_host_object(product)
            self.assertEqual(data, {})
            normalize_local.assert_called_once_with(product)
        self.assertEqual(data, importer.normalize_local_object(product))


class TestAdminUser(DualRattailTestCase):

    importer_class = rattail_importing.AdminUserImporter

    def make_importer(self, **kwargs):
        kwargs.setdefault('session', self.session)
        return self.importer_class(**kwargs)

    def get_admin(self):
        return auth.administrator_role(self.session)

    def test_normalize_host_object(self):
        importer = self.make_importer()
        user = model.User()
        data = importer.normalize_host_object(user)
        self.assertFalse(data['admin'])
        user.roles.append(self.get_admin())
        data = importer.normalize_host_object(user)
        self.assertTrue(data['admin'])
