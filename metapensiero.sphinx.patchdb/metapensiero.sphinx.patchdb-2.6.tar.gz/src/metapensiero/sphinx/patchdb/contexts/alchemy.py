# -*- coding: utf-8 -*-
# :Project:   PatchDB -- SQLAlchemy script execution context
# :Created:   sab 31 mag 2014 13:05:23 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016 Lele Gaifax
#

from __future__ import unicode_literals

from . import logger
from .sql import SqlContext


class SQLAlchemyContext(SqlContext):
    def makeConnection(self, url):
        from sqlalchemy import create_engine

        self.url = url
        logger.debug('Connecting to %s', self.url)
        self.engine = create_engine(self.url)
        self.connection = self.engine.connect().connection

    def setupContext(self):
        from sqlalchemy import (Column, DateTime, MetaData, SmallInteger,
                                String, Table)
        from ..patch import MAX_PATCHID_LEN

        metadata = MetaData()
        self.applied_info = Table('patchdb', metadata,
                                  Column('patchid', String(MAX_PATCHID_LEN),
                                         nullable=False, primary_key=True),
                                  Column('revision', SmallInteger, nullable=False),
                                  Column('applied', DateTime, nullable=False))
        metadata.create_all(self.engine)

    @property
    def patches(self):
        """
        Extract the applied info from the database, returning a
        dictionary mapping a patch id to its revision.
        """

        from sqlalchemy import select

        if self._patches is None:
            self._patches = dict((pid.decode('utf-8'), rev)
                                 for pid,rev in self.engine.execute(
                                    select([self.applied_info.c.patchid,
                                            self.applied_info.c.revision])))
        return self._patches

    def _recordAppliedInfo(self, pid, rev):
        """Persist the knowledge on the database."""

        from datetime import datetime
        from sqlalchemy import select

        pid = pid.encode('utf-8')
        apprev = self.engine.execute(
            select([self.applied_info.c.revision],
                   self.applied_info.c.patchid==pid)).scalar()
        now = datetime.now()

        if apprev is None:
            logger.debug('Inserting "%s@%s" into the database', pid, rev)
            self.engine.execute(self.applied_info.insert()
                                .values(patchid=pid, revision=rev, applied=now))
        else:
            logger.debug('Updating "%s@%s" in the database', pid, rev)
            self.engine.execute(self.applied_info.update()
                                .where(self.applied_info.c.patchid==pid)
                                .values(revision=rev, applied=now))
        self[pid] = rev
