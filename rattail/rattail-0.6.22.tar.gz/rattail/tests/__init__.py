# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import warnings
from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.exc import SAWarning

from rattail.db import model
from rattail.db import Session


warnings.filterwarnings(
    'ignore',
    r"^Dialect sqlite\+pysqlite does \*not\* support Decimal objects natively\, "
    "and SQLAlchemy must convert from floating point - rounding errors and other "
    "issues may occur\. Please consider storing Decimal numbers as strings or "
    "integers on this platform for lossless storage\.$",
    SAWarning, r'^sqlalchemy\..*$')


class DataTestCase(TestCase):

    engine_url = os.environ.get('RATTAIL_TEST_ENGINE_URL', 'sqlite://')

    def setUp(self):
        self.engine = create_engine(self.engine_url)
        model.Base.metadata.create_all(bind=self.engine)
        Session.configure(bind=self.engine)
        self.session = Session()
        self.extra_setup()

    def extra_setup(self):
        """
        Derivative classes may define this as necessary, to avoid having to
        override the :meth:`setUp()` method.
        """

    def tearDown(self):
        self.session.close()
        Session.configure(bind=None)
        model.Base.metadata.drop_all(bind=self.engine)

        # # TODO: This doesn't seem to be necessary, hopefully that's good?
        # for table in list(model.Base.metadata.sorted_tables):
        #     if table.name.startswith('batch.'):
        #         model.Base.metadata.remove(table)

        # TODO: Unfortunately this *does* seem to be necessary...
        model.Batch._rowclasses.clear()
