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
Import Handlers
"""

from __future__ import unicode_literals, absolute_import

import logging

from rattail.util import OrderedDict
from rattail.mail import send_email


log = logging.getLogger(__name__)


class ImportHandler(object):
    """
    Base class for all import handlers.
    """

    def __init__(self, config=None, session=None):
        self.config = config
        self.session = session
        self.importers = self.get_importers()

    def get_importers(self):
        """
        Returns a dict of all available importers, where the values are
        importer factories.  All subclasses will want to override this.  Note
        that if you return an ``OrderedDict`` instance, you can affect the
        ordering of keys in the command line help system, etc.
        """
        return {}

    def get_importer_keys(self):
        """
        Returns a list of keys corresponding to the available importers.
        """
        return list(self.importers.iterkeys())

    def get_importer(self, key):
        """
        Returns an importer instance corresponding to the given key.
        """
        return self.importers[key](self.config, self.session,
                                   **self.get_importer_kwargs(key))

    def get_importer_kwargs(self, key):
        """
        Return a dict of kwargs to be used when construcing an importer with
        the given key.
        """
        return {}

    def import_data(self, keys, max_updates=None, progress=None):
        """
        Import all data for the given importer keys.
        """
        self.before_import()
        updates = OrderedDict()

        for key in keys:
            provider = self.get_importer(key)
            if not provider:
                log.warning("unknown importer; skipping: {0}".format(repr(key)))
                continue

            data = provider.get_data(progress=progress)
            created, updated = provider.importer.import_data(
                data, provider.supported_fields, provider.key,
                max_updates=max_updates, progress=progress)

            if hasattr(provider, 'process_deletions'):
                deleted = provider.process_deletions(data, progress=progress)
            else:
                deleted = 0

            log.info("added {0}, updated {1}, deleted {2} {3} records".format(
                len(created), len(updated), deleted, key))
            if created or updated or deleted:
                updates[key] = created, updated, deleted

        self.after_import()
        return updates

    def before_import(self):
        return 

    def after_import(self):
        return 

    def process_warnings(self, updates, command=None, **kwargs):
        """
        If an import was run with "warnings" enabled, and work was effectively
        done then this method is called to process the updates.  The assumption
        is that a warning email will be sent with the details, but you can do
        anything you like if you override this.
        """
        data = kwargs
        data['updates'] = updates

        if command:
            data['command'] = '{} {}'.format(command.parent.name, command.name)
        else:
            data['command'] = None

        if command:
            key = '{}_{}_updates'.format(command.parent.name, command.name)
            key = key.replace('-', '_')
        else:
            key = 'rattail_import_updates'

        send_email(self.config, key, fallback_key='rattail_import_updates', data=data)
