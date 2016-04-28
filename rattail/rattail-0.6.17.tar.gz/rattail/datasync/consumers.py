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
DataSync Consumers
"""

from __future__ import unicode_literals, absolute_import

from rattail.config import parse_list
from rattail.db.newimporting import ImportHandler


class DataSyncConsumer(object):
    """
    Base class for all DataSync consumers.
    """

    def __init__(self, config, key, dbkey=None):
        self.config = config
        self.key = key
        self.dbkey = dbkey

    def setup(self):
        """
        This method is called when the consumer thread is first started.
        """

    def begin_transaction(self):
        """
        Called just before the consumer is asked to process changes, possibly
        via multiple batches.
        """

    def process_changes(self, session, changes):
        """
        Process (consume) a batch of changes.
        """

    def rollback_transaction(self):
        """
        Called when any batch of changes failed to process.
        """

    def commit_transaction(self):
        """
        Called just after the consumer has successfully finished processing
        changes, possibly via multiple batches.
        """


class DataSyncImportConsumer(DataSyncConsumer):
    """
    Base class for DataSync consumer which is able to leverage a (set of)
    importer(s) to do the heavy lifting.
    """

    def __init__(self, *args, **kwargs):
        super(DataSyncImportConsumer, self).__init__(*args, **kwargs)
        self.importers = self.get_importers()

    def get_importers(self):
        """
        You must override this to return a dict of importer *instances*, keyed
        by what you expect the corresponding ``DataSyncChange.payload_type`` to
        be, coming from the "host" system, whatever that is.
        """
        raise NotImplementedError

    def get_importers_from_handler(self, handler, default_only=True):
        if not isinstance(handler, ImportHandler):
            handler = handler(config=self.config)
        factories = handler.get_importers()
        if default_only:
            keys = handler.get_default_keys()
        else:
            keys = factories.keys()
        importers = {}
        for key in keys:
            importers[key] = factories[key](config=self.config)
        return importers

    def process_changes(self, session, changes):
        """
        Process all changes, leveraging importer(s) as much as possible.
        """
        # Update all importers with current Rattail session.
        for importer in self.importers.itervalues():
            importer.session = session

        for change in changes:
            self.invoke_importer(session, change)

    def invoke_importer(self, session, change):
        """
        For the given change, invoke the default importer behavior, if one is
        available.
        """
        importer = self.importers.get(change.payload_type)
        if importer:
            if change.deletion:
                self.process_deletion(session, importer, change)
            else:
                return self.process_change(session, importer, change)

    def process_change(self, session, importer, change=None, host_object=None, host_data=None):
        """
        Invoke the importer to process the given change / host record.
        """
        if host_data is None:
            if host_object is None:
                host_object = self.get_host_record(session, change)
                if host_object is None:
                    return
            host_data = importer.normalize_source_record(host_object)
            if host_data is None:
                return
        key = importer.get_key(host_data)
        local_object = importer.get_instance(key)
        if local_object:
            local_data = importer.normalize_instance(local_object)
            if importer.data_diffs(local_data, host_data):
                local_object = importer.update_instance(local_object, host_data, local_data)
            return local_object
        else:
            return importer.create_instance(key, host_data)

    def process_deletion(self, session, importer, change):
        """
        Attempt to invoke the importer, to delete a local record according to
        the change involved.
        """
        key = self.get_deletion_key(session, change)
        local_object = importer.get_instance(key)
        if local_object:
            return importer.delete_instance(local_object)
        return False

    def get_deletion_key(self, session, change):
        return (change.payload_key,)

    def get_host_record(self, session, change):
        """
        You must override this, to return a host record from the given
        ``DataSyncChange`` instance.  Note that the host record need *not* be
        normalized, as that will be done by the importer.  (This is effectively
        the only part of the processing which is not handled by the importer.)
        """
        raise NotImplementedError


class ErrorTestConsumer(DataSyncConsumer):
    """
    Consumer which always raises an error when processing changes.  Useful for
    testing error handling etc.
    """

    def process_changes(self, session, changes):
        raise RuntimeError("Fake exception, to test error handling")
