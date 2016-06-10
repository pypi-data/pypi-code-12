# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

from unittest import TestCase

from mock import patch

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm.exc import MultipleResultsFound

from rattail.importing import sqlalchemy as saimport


class Widget(object):
    pass

metadata = sa.MetaData()

widget_table = sa.Table('widgets', metadata,
                        sa.Column('id', sa.Integer(), primary_key=True),
                        sa.Column('description', sa.String(length=50)))

widget_mapper = orm.mapper(Widget, widget_table)

WIDGETS = [
    {'id': 1, 'description': "Main Widget"},
    {'id': 2, 'description': "Other Widget"},
    {'id': 3, 'description': "Other Widget"},
]


class TestFromSQLAlchemy(TestCase):

    def test_query(self):
        Session = orm.sessionmaker(bind=sa.create_engine('sqlite://'))
        session = Session()
        importer = saimport.FromSQLAlchemy(host_session=session,
                                           host_model_class=Widget)
        self.assertEqual(unicode(importer.query()),
                         "SELECT widgets.id AS widgets_id, widgets.description AS widgets_description \n"
                         "FROM widgets")


class TestToSQLAlchemy(TestCase):

    def setUp(self):
        engine = sa.create_engine('sqlite://')
        metadata.create_all(bind=engine)
        Session = orm.sessionmaker(bind=engine)
        self.session = Session()
        for data in WIDGETS:
            widget = Widget()
            for key, value in data.iteritems():
                setattr(widget, key, value)
            self.session.add(widget)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        del self.session

    def make_importer(self, **kwargs):
        kwargs.setdefault('model_class', Widget)
        return saimport.ToSQLAlchemy(**kwargs)

    def test_model_mapper(self):
        importer = self.make_importer()
        self.assertIs(importer.model_mapper, widget_mapper)

    def test_model_table(self):
        importer = self.make_importer()
        self.assertIs(importer.model_table, widget_table)

    def test_simple_fields(self):
        importer = self.make_importer()
        self.assertEqual(importer.simple_fields, ['id', 'description'])

    def test_get_single_local_object(self):

        # simple key
        importer = self.make_importer(key='id', session=self.session)
        widget = importer.get_single_local_object((1,))
        self.assertEqual(widget.id, 1)
        self.assertEqual(widget.description, "Main Widget")

        # compound key
        importer = self.make_importer(key=('id', 'description'), session=self.session)
        widget = importer.get_single_local_object((1, "Main Widget"))
        self.assertEqual(widget.id, 1)
        self.assertEqual(widget.description, "Main Widget")

        # widget not found
        importer = self.make_importer(key='id', session=self.session)
        self.assertIsNone(importer.get_single_local_object((42,)))

        # multiple widgets found
        importer = self.make_importer(key='description', session=self.session)
        self.assertRaises(MultipleResultsFound, importer.get_single_local_object, ("Other Widget",))

    def test_create_object(self):
        importer = self.make_importer(key='id', session=self.session)
        widget = importer.create_object((42,), {'id': 42, 'description': "Latest Widget"})
        self.assertIn(widget, self.session)
        self.assertIn(widget, self.session.new)
        self.assertEqual(widget.id, 42)
        self.assertEqual(widget.description, "Latest Widget")

    def test_delete_object(self):
        widget = self.session.query(Widget).get(1)
        self.assertIn(widget, self.session)
        importer = self.make_importer(session=self.session)
        self.assertTrue(importer.delete_object(widget))
        self.assertIn(widget, self.session)
        self.assertIn(widget, self.session.deleted)
        self.session.flush()
        self.assertIsNone(self.session.query(Widget).get(1))

    def test_cache_model(self):
        importer = self.make_importer(key='id', session=self.session)
        cache = importer.cache_model(Widget, key='id')
        self.assertEqual(len(cache), 3)
        for i in range(1, 4):
            self.assertIn(i, cache)
            self.assertIsInstance(cache[i], Widget)
            self.assertEqual(cache[i].id, i)
            self.assertEqual(cache[i].description, WIDGETS[i-1]['description'])

    def test_cache_local_data(self):
        importer = self.make_importer(key='id', session=self.session)
        cache = importer.cache_local_data()
        self.assertEqual(len(cache), 3)
        for i in range(1, 4):
            self.assertIn((i,), cache)
            cached = cache[(i,)]
            self.assertIsInstance(cached, dict)
            self.assertIsInstance(cached['object'], Widget)
            self.assertEqual(cached['object'].id, i)
            self.assertEqual(cached['object'].description, WIDGETS[i-1]['description'])
            self.assertIsInstance(cached['data'], dict)
            self.assertEqual(cached['data']['id'], i)
            self.assertEqual(cached['data']['description'], WIDGETS[i-1]['description'])

    # TODO: lame
    def test_flush_session(self):
        importer = self.make_importer(fields=['id'], key='id', session=self.session, flush_session=True)
        widget = Widget()
        widget.id = 1
        widget, original = importer.update_object(widget, {'id': 1}), widget
        self.assertIs(widget, original)

    def test_flush_create_update(self):
        importer = saimport.ToSQLAlchemy(fields=['id'], session=self.session)
        with patch.object(self.session, 'flush') as flush:
            importer.flush_create_update()
            flush.assert_called_once_with()
