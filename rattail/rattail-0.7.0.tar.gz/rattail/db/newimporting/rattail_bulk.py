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
Rattail -> Rattail bulk data import
"""

from __future__ import unicode_literals, absolute_import

import os

from rattail.db import Session, newimporting as importing
from rattail.util import OrderedDict


class RattailImportHandler(importing.BulkPostgreSQLImportHandler):
    """
    Handler for Rattail -> Rattail bulk data import.
    """
    host_title = "Rattail"
    dbkey = 'host'

    def make_host_session(self):
        return Session(bind=self.config.rattail_engines[self.dbkey])

    def get_importers(self):
        importers = OrderedDict()
        importers['ScheduledShift'] = ScheduledShiftImporter
        importers['WorkedShift'] = WorkedShiftImporter
        return importers

    def get_importer_kwargs(self, key):
        kwargs = super(RattailImportHandler, self).get_importer_kwargs(key)
        kwargs['dbkey'] = self.dbkey
        return kwargs


class RattailImporter(importing.SQLAlchemyImporter, importing.BulkPostgreSQLImporter):
    """
    Base class for Rattail -> Rattail bulk data importers.
    """

    @property
    def host_model_class(self):
        return self.model_class

    @property
    def supported_fields(self):
        """
        We only need to support the simple fields in a Rattail->Rattail import,
        since all relevant tables should be covered and therefore no need to do
        crazy foreign key acrobatics etc.
        """
        return self.simple_fields

    @property
    def data_path(self):
        return os.path.join(self.config.require('rattail', 'workdir'),
                            'import_{}.csv'.format(self.model_table.name))

    @property
    def normalize_progress_message(self):
        return "Reading {} data from '{}' db".format(self.model_name, self.dbkey)

    def query(self):
        query = super(RattailImporter, self).query()
        options = self.cache_query_options()
        if options:
            for option in options:
                query = query.options(option)
        return query

    def normalize_source_record(self, host_object):
        return self.normalize_instance(host_object)


class ScheduledShiftImporter(RattailImporter, importing.model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(RattailImporter, importing.model.WorkedShiftImporter):
    pass
