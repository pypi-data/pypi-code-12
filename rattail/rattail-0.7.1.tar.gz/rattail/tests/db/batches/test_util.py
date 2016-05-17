# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import datetime

import sqlalchemy as sa

from rattail.db import model
from rattail.db.batches import util
from rattail.tests import DataTestCase


class TestPurgeBatches(DataTestCase):

    def setUp(self):
        super(TestPurgeBatches, self).setUp()

        batch = model.Batch(purge=datetime.date(2014, 1, 1))
        batch.add_column('F01')
        batch.add_column('F02')
        self.session.add(batch)
        batch.create_table()

        batch = model.Batch(purge=datetime.date(2014, 2, 1))
        batch.add_column('F01')
        batch.add_column('F02')
        self.session.add(batch)
        batch.create_table()

        batch = model.Batch(purge=datetime.date(2014, 3, 1))
        batch.add_column('F01')
        batch.add_column('F02')
        self.session.add(batch)
        batch.create_table()

        self.session.commit()

    def get_batch_tables_metadata(self):
        def batch_tables(name, metadata):
            return util.batch_pattern.match(name)
        metadata = sa.MetaData(bind=self.engine)
        metadata.reflect(only=batch_tables)
        return metadata

    def test_purging_honors_batch_purge_dates(self):
        self.assertEqual(self.session.query(model.Batch).count(), 3)
        self.assertEqual(util.purge_batches(effective_date=datetime.date(2014, 1, 15)), 1)
        self.assertEqual(self.session.query(model.Batch).count(), 2)
        self.assertEqual(self.session.query(sa.func.min(model.Batch.purge)).scalar(), datetime.date(2014, 2, 1))

    def test_purging_everything_does_just_that(self):
        self.assertEqual(self.session.query(model.Batch).count(), 3)
        self.assertEqual(util.purge_batches(purge_everything=True), 3)
        self.assertEqual(self.session.query(model.Batch).count(), 0)

    # TODO: The next two tests each work if only one is enabled...but if both
    # are enabled, one will fail.  This needs more investigation, but one
    # possible cause is the "corruption" of Base.metadata when Batch.rowclass
    # is accessed?  In particular it seems *not* to be a SQLite problem, as it
    # occurred when using a PostgreSQL engine as well.

    # def test_purging_does_not_leave_orphaned_tables(self):
    #     self.assertEqual(self.session.query(model.Batch).count(), 3)
    #     self.assertEqual(util.purge_batches(purge_everything=True), 3)
    #     self.assertEqual(self.session.query(model.Batch).count(), 0)
    #     metadata = self.get_batch_tables_metadata()
    #     self.assertEqual(len(metadata.tables), 0)

    # def test_purging_does_not_delete_previously_orphaned_tables(self):
    #     metadata = self.get_batch_tables_metadata()
    #     self.assertEqual(len(metadata.tables), 3)
    #     batch = self.session.query(model.Batch).first()
    #     batch.drop_table()
    #     self.assertEqual(self.session.query(model.Batch).count(), 3)
    #     metadata = self.get_batch_tables_metadata()
    #     self.assertEqual(len(metadata.tables), 2)
