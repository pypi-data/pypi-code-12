# -*- coding: utf-8 -*-
# :Project:   PatchDB -- PostgreSQL script execution context
# :Created:   sab 31 mag 2014 13:03:33 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2014, 2016 Lele Gaifax
#

from __future__ import unicode_literals

from os import makedirs
from os.path import isdir, join
import subprocess

from ..states import StatesIndex
from . import logger
from .sql import SqlContext


class PostgresContext(SqlContext):
    def makeConnection(self, dsn):
        import psycopg2 as dbapi
        import re

        self.dsn = dsn
        logger.debug('Connecting to %s', self.dsn)
        self.connection = dbapi.connect(self.dsn)
        cursor = self.connection.cursor()
        cursor.execute("set client_encoding to unicode;")

        cursor.execute("SELECT version()")
        v = cursor.fetchone()
        m = re.match('PostgreSQL (\d+)\.(\d+)\.(\d+)', v[0])
        if m is None:
            # Maybe a beta?
            m = re.match('PostgreSQL (\d+)\.(\d+)(beta\d+)', v[0])
        assert m, "Could not determine PostgreSQL version"
        pg_version = tuple([int(x) for x in m.group(1, 2)])

        self.assertions.update({
            'postgres': True,
            'postgres_9_x': (9,0) <= pg_version < (10,0),
            'postgres_8_x': (8,0) <= pg_version < (9,0),
            'postgres_7_x': (7,0) <= pg_version < (8,0),
            'postgresql': True,
            'postgresql_9_x': (9,0) <= pg_version < (10,0),
            'postgresql_8_x': (8,0) <= pg_version < (9,0),
            'postgresql_7_x': (7,0) <= pg_version < (8,0),
            })

    def setupContext(self):
        from ..patch import MAX_PATCHID_LEN

        cursor = self.connection.cursor()
        cursor.execute("SELECT tablename"
                       " FROM pg_tables"
                       " WHERE tablename = 'patchdb'")
        result = cursor.fetchone()
        if not result:
            logger.info('Creating patchdb table')
            cursor.execute("CREATE TABLE patchdb ("
                           " patchid VARCHAR(%d) NOT NULL PRIMARY KEY,"
                           " revision SMALLINT NOT NULL,"
                           " applied TIMESTAMP WITH TIME ZONE NOT NULL"
                           ")" % MAX_PATCHID_LEN)
            self.connection.commit()

    def savePoint(self, point):
        cursor = self.connection.cursor()
        cursor.execute("savepoint point_%s" % point)

    def rollbackPoint(self, point):
        cursor = self.connection.cursor()
        cursor.execute("rollback to savepoint point_%s" % point)

    def classifyError(self, exc):
        msg = exc.pgerror
        if hasattr(msg, 'decode'):
            try:
                msg = msg.decode('utf-8')
            except UnicodeDecodeError:
                msg = msg.decode('latin1', 'ignore')
        code = exc.pgcode
        msg = '[%s] %s' % (code, msg)
        # See http://www.postgresql.org/docs/9.3/static/errcodes-appendix.html
        syntaxerror = code in ('42000', '42601')
        nonexistingobj = code in ('42883', '42P01', '42704')
        return msg, syntaxerror, nonexistingobj

    def backup(self, dir):
        state = self.state
        if state is None:
            logger.debug("Skipping initial backup")
            return

        if not isdir(dir):
            makedirs(dir)

        outfname = join(dir, state.state)
        cmd = ['pg_dump', '-d', self.dsn, '-Fc', '-Z9', '-f', outfname]
        subprocess.check_call(cmd)

        with StatesIndex(dir) as index:
            index.append(state)

        logger.info("Wrote pg_dump compressed backup to %s", outfname)

    def restore(self, backup):
        cmd = ['pg_restore', '-d', self.dsn, '-c', backup]
        subprocess.check_call(cmd)
        logger.info("Restored PostgreSQL database from %s", backup)
