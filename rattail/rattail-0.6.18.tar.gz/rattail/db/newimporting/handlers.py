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

import sys
import datetime
import logging

import humanize

from rattail.util import OrderedDict
from rattail.mail import send_email


log = logging.getLogger(__name__)


class ImportHandler(object):
    """
    Base class for all import handlers.
    """
    local_title = "Rattail"
    host_title = "Host/Other"
    session = None
    progress = None
    dry_run = False

    def __init__(self, config=None, **kwargs):
        self.config = config
        self.importers = self.get_importers()
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

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

    def get_default_keys(self):
        """
        Returns a list of keys corresponding to the default importers.
        Override this if you wish certain importers to be excluded by default,
        e.g. when first testing them out etc.
        """
        return self.get_importer_keys()

    def get_importer(self, key):
        """
        Returns an importer instance corresponding to the given key.
        """
        kwargs = self.get_importer_kwargs(key)
        kwargs['config'] = self.config
        kwargs['session'] = self.session
        importer = self.importers[key](**kwargs)
        importer.handler = self
        return importer

    def get_importer_kwargs(self, key):
        """
        Return a dict of kwargs to be used when construcing an importer with
        the given key.
        """
        kwargs = {}
        if hasattr(self, 'host_session'):
            kwargs['host_session'] = self.host_session
        return kwargs

    def import_data(self, keys, args):
        """
        Import all data for the given importer keys.
        """
        self.now = datetime.datetime.utcnow()
        self.dry_run = args.dry_run
        self.begin_transaction()
        self.setup()
        changes = OrderedDict()

        for key in keys:
            importer = self.get_importer(key)
            if not importer:
                log.warning("skipping unknown importer: {}".format(key))
                continue

            created, updated, deleted = importer.import_data(args, progress=self.progress)

            changed = bool(created or updated or deleted)
            logger = log.warning if changed and args.warnings else log.info
            logger("{} -> {}: added {}, updated {}, deleted {} {} records".format(
                self.host_title, self.local_title, len(created), len(updated), len(deleted), key))
            if changed:
                changes[key] = created, updated, deleted

        if changes:
            self.process_changes(changes, args)

        if self.dry_run:
            self.rollback_transaction()
        else:
            self.commit_transaction()

        self.teardown()
        return changes

    def begin_transaction(self):
        self.begin_host_transaction()
        self.begin_local_transaction()

    def begin_host_transaction(self):
        if hasattr(self, 'make_host_session'):
            self.host_session = self.make_host_session()

    def begin_local_transaction(self):
        pass

    def setup(self):
        """
        Perform any setup necessary, prior to running the import task(s).
        """

    def rollback_transaction(self):
        self.rollback_host_transaction()
        self.rollback_local_transaction()

    def rollback_host_transaction(self):
        if hasattr(self, 'host_session'):
            self.host_session.rollback()
            self.host_session.close()
            self.host_session = None

    def rollback_local_transaction(self):
        pass

    def commit_transaction(self):
        self.commit_host_transaction()
        self.commit_local_transaction()

    def commit_host_transaction(self):
        if hasattr(self, 'host_session'):
            self.host_session.commit()
            self.host_session.close()
            self.host_session = None

    def commit_local_transaction(self):
        pass

    def teardown(self):
        """
        Perform any cleanup necessary, after running the import task(s).
        """

    def process_changes(self, changes, args):
        """
        This method is called any time changes occur, regardless of whether the
        import is running in "warnings" mode.  Default implementation however
        is to do nothing unless warnings mode is in effect, in which case an
        email notification will be sent.
        """
        # TODO: This whole thing needs a re-write...but for now, waiting until
        # the old importer has really gone away, so we can share its email
        # template instead of bothering with something more complicated.

        if not args.warnings:
            return

        data = {
            'local_title': self.local_title,
            'host_title': self.host_title,
            'argv': sys.argv,
            'runtime': humanize.naturaldelta(datetime.datetime.utcnow() - self.now),
            'changes': changes,
            'dry_run': args.dry_run,
            'render_record': RecordRenderer(self.config),
            'max_display': 15,
        }

        command = getattr(self, 'command', None)
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


class SQLAlchemyImportHandler(ImportHandler):
    """
    Handler for imports for which the host data source is represented by a
    SQLAlchemy engine and ORM.
    """
    host_session = None

    def make_host_session(self):
        raise NotImplementedError


class BulkPostgreSQLImportHandler(ImportHandler):
    """
    Handler for bulk imports which target PostgreSQL on the local side.
    """

    def import_data(self, keys, args):
        """
        Import all data for the given importer keys.
        """
        self.now = datetime.datetime.utcnow()
        self.dry_run = args.dry_run
        self.begin_transaction()
        self.setup()

        for key in keys:
            importer = self.get_importer(key)
            if not importer:
                log.warning("skipping unknown importer: {}".format(key))
                continue

            created = importer.import_data(args, progress=self.progress)
            log.info("{} -> {}: added {}, updated 0, deleted 0 {} records".format(
                self.host_title, self.local_title, created, key))

        if self.dry_run:
            self.rollback_transaction()
        else:
            self.commit_transaction()

        self.teardown()


class RecordRenderer(object):
    """
    Record renderer for email notifications sent from data import jobs.
    """

    def __init__(self, config):
        self.config = config

    def __call__(self, record):
        return self.render(record)

    def render(self, record):
        """
        Render the given record.
        """
        key = record.__class__.__name__.lower()
        renderer = getattr(self, 'render_{}'.format(key), None)
        if renderer:
            return renderer(record)

        label = self.get_label(record)
        url = self.get_url(record)
        if url:
            return '<a href="{}">{}</a>'.format(url, label)
        return label

    def get_label(self, record):
        key = record.__class__.__name__.lower()
        label = getattr(self, 'label_{}'.format(key), self.label)
        return label(record)

    def label(self, record):
        return unicode(record)

    def get_url(self, record):
        """
        Fetch / generate a URL for the given data record.  You should *not*
        override this method, but do :meth:`url()` instead.
        """
        key = record.__class__.__name__.lower()
        url = getattr(self, 'url_{}'.format(key), self.url)
        return url(record)

    def url(self, record):
        """
        Fetch / generate a URL for the given data record.
        """
        if hasattr(record, 'uuid'):
            url = self.config.get('tailbone', 'url')
            if url:
                url = url.rstrip('/')
                name = '{}s'.format(record.__class__.__name__.lower())
                if name == 'persons': # FIXME, obviously this is a hack
                    name = 'people'
                url = '{}/{}/{{uuid}}'.format(url, name)
                return url.format(uuid=record.uuid)
