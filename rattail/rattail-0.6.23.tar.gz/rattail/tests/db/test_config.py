# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import warnings
from unittest import TestCase

from sqlalchemy.pool import SingletonThreadPool, NullPool

from rattail.config import make_config
from rattail.db import config as dbconfig


class TestEngineConfig(TestCase):

    def test_standard(self):
        config = {
            'sqlalchemy.url': 'sqlite://',
            }
        engine = dbconfig.engine_from_config(config)
        self.assertEqual(str(engine.url), 'sqlite://')
        self.assertTrue(isinstance(engine.pool, SingletonThreadPool))

    def test_custom_poolclass(self):
        config = {
            'sqlalchemy.url': 'sqlite://',
            'sqlalchemy.poolclass': 'sqlalchemy.pool:NullPool',
            }
        engine = dbconfig.engine_from_config(config)
        self.assertEqual(str(engine.url), 'sqlite://')
        self.assertTrue(isinstance(engine.pool, NullPool))


class TestGetEngines(TestCase):

    def setUp(self):
        self.config = make_config([])

    def test_default_section_is_rattail_db(self):
        self.config.set(u'rattail.db', u'keys', u'default')
        self.config.set(u'rattail.db', u'default.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(engines.keys()[0], u'default')
        self.assertEqual(unicode(engines[u'default'].url), u'sqlite://')

    def test_custom_section_is_honored(self):
        self.config.set(u'mycustomdb', u'keys', u'default')
        self.config.set(u'mycustomdb', u'default.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config, section=u'mycustomdb')
        self.assertEqual(len(engines), 1)
        self.assertEqual(engines.keys()[0], u'default')
        self.assertEqual(unicode(engines[u'default'].url), u'sqlite://')

    def test_default_prefix_does_not_require_keys_declaration(self):
        self.config.set(u'rattail.db', u'default.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(engines.keys()[0], u'default')
        self.assertEqual(unicode(engines[u'default'].url), u'sqlite://')

    def test_default_prefix_falls_back_to_sqlalchemy(self):
        # Still no need to define "keys" option here.
        self.config.set(u'rattail.db', u'sqlalchemy.url', u'sqlite://')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 1)
        self.assertEqual(engines.keys()[0], u'default')
        self.assertEqual(unicode(engines[u'default'].url), u'sqlite://')

    def test_defined_keys_are_included_in_engines_result(self):
        # Note there is no "default" key here.
        self.config.set(u'rattail.db', u'keys', u'host, store')
        self.config.set(u'rattail.db', u'host.url', u'sqlite:///rattail.host.sqlite')
        self.config.set(u'rattail.db', u'store.url', u'sqlite:///rattail.store.sqlite')
        engines = dbconfig.get_engines(self.config)
        self.assertEqual(len(engines), 2)
        self.assertEqual(sorted(engines.keys()), [u'host', u'store'])
        self.assertEqual(unicode(engines[u'host'].url), u'sqlite:///rattail.host.sqlite')
        self.assertEqual(unicode(engines[u'store'].url), u'sqlite:///rattail.store.sqlite')


class TestGetDefaultEngine(TestCase):

    def setUp(self):
        self.config = make_config([])

    def test_default_engine_is_loaded_from_rattail_db_section_by_default(self):
        self.config.set(u'rattail.db', u'keys', u'default')
        self.config.set(u'rattail.db', u'default.url', u'sqlite://')
        engine = dbconfig.get_default_engine(self.config)
        self.assertEqual(unicode(engine.url), u'sqlite://')

    def test_default_engine_is_loaded_from_custom_section_if_specified(self):
        self.config.set(u'mycustomdb', u'keys', u'default')
        self.config.set(u'mycustomdb', u'default.url', u'sqlite://')
        engine = dbconfig.get_default_engine(self.config, section=u'mycustomdb')
        self.assertEqual(unicode(engine.url), u'sqlite://')

    def test_no_engine_is_returned_if_none_is_defined(self):
        engine = dbconfig.get_default_engine(self.config)
        self.assertTrue(engine is None)
