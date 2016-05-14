# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
PostgreSQL data importers
"""

from __future__ import unicode_literals, absolute_import

import os
import datetime
import logging

from rattail.importing.sqlalchemy import ToSQLAlchemy
from rattail.time import make_utc


log = logging.getLogger(__name__)


class BulkToPostgreSQL(ToSQLAlchemy):
    """
    Base class for bulk data importers which target PostgreSQL on the local side.
    """

    @property
    def data_path(self):
        return os.path.join(self.config.workdir(require=True),
                            'import_bulk_postgresql_{}.csv'.format(self.model_name))

    def setup(self):
        self.data_buffer = open(self.data_path, 'wb')

    def teardown(self):
        self.data_buffer.close()
        os.remove(self.data_path)
        self.data_buffer = None

    def import_data(self, host_data=None, now=None, **kwargs):
        self.now = now or make_utc(datetime.datetime.utcnow(), tzinfo=True)
        if kwargs:
            self._setup(**kwargs)
        self.setup()
        if host_data is None:
            host_data = self.normalize_host_data()
        created = self._import_create(host_data)
        self.teardown()
        return created

    def _import_create(self, data):
        count = len(data)
        if not count:
            return 0
        created = count

        prog = None
        if self.progress:
            prog = self.progress("Importing {} data".format(self.model_name), count)

        for i, host_data in enumerate(data, 1):

            key = self.get_key(host_data)
            self.create_object(key, host_data)
            if self.max_create and i >= self.max_create:
                log.warning("max of {} *created* records has been reached; stopping now".format(self.max_create))
                created = i
                break

            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        self.commit_create()
        return created

    def create_object(self, key, data):
        data = self.prep_data_for_postgres(data)
        self.data_buffer.write('{}\n'.format('\t'.join([data[field] for field in self.fields])).encode('utf-8'))

    def prep_data_for_postgres(self, data):
        data = dict(data)
        for key, value in data.iteritems():
            data[key] = self.prep_value_for_postgres(value)
        return data

    def prep_value_for_postgres(self, value):
        if value is None:
            return '\\N'
        if value is True:
            return 't'
        if value is False:
            return 'f'

        if isinstance(value, datetime.datetime):
            value = make_utc(value, tzinfo=False)
        elif isinstance(value, basestring):
            value = value.replace('\\', '\\\\')
            value = value.replace('\r', '\\r')
            value = value.replace('\n', '\\n')
            value = value.replace('\t', '\\t') # TODO: add test for this

        return unicode(value)

    def commit_create(self):
        log.info("copying {} data from buffer to PostgreSQL".format(self.model_name))
        self.data_buffer.close()
        self.data_buffer = open(self.data_path, 'rb')
        cursor = self.session.connection().connection.cursor()
        table_name = '"{}"'.format(self.model_table.name)
        cursor.copy_from(self.data_buffer, table_name, columns=self.fields)
        log.debug("PostgreSQL data copy completed")
