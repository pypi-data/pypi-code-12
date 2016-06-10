# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from unittest import TestCase

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rattail.db import model


class SyncTestCase(TestCase):

    def setUp(self):
        self.local_engine = create_engine('sqlite://')
        self.remote_engines = {
            'one': create_engine('sqlite://'),
            'two': create_engine('sqlite://'),
            }
        self.Session = sessionmaker()
        model.Base.metadata.create_all(bind=self.local_engine)
        model.Base.metadata.create_all(bind=self.remote_engines['one'])
        model.Base.metadata.create_all(bind=self.remote_engines['two'])
