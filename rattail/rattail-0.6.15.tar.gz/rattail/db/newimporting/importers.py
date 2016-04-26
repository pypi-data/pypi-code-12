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
Data Importers
"""

from __future__ import unicode_literals, absolute_import

import datetime
import logging

from sqlalchemy import orm
from sqlalchemy.orm.exc import NoResultFound

from rattail.db import cache
from rattail.time import make_utc


log = logging.getLogger(__name__)


class Importer(object):
    """
    Base class for all data importers.
    """
    key = 'uuid'
    cached_instances = None
    allow_create = True
    allow_update = True
    allow_delete = True
    dry_run = False

    def __init__(self, config=None, session=None, fields=None, key=None, **kwargs):
        self.config = config
        self.session = session
        self.fields = fields or self.supported_fields
        if key:
            self.key = key
        if isinstance(self.key, basestring):
            self.key = (self.key,)
        for key, value in kwargs.iteritems():
            setattr(self, key, value)

    @property
    def model_class(self):
        """
        This should return a reference to the model class which the importer
        "targets" so to speak.
        """
        raise NotImplementedError

    @property
    def model_name(self):
        """
        Returns the string 'name' of the model class which the importer targets.
        """
        return self.model_class.__name__

    @property
    def model_mapper(self):
        """
        This should return the SQLAlchemy mapper for the model class.
        """
        return orm.class_mapper(self.model_class)

    @property
    def model_table(self):
        """
        Returns the underlying table used by the primary local data model class.
        """
        tables = self.model_mapper.tables
        assert len(tables) == 1
        return tables[0]

    @property
    def simple_fields(self):
        """
        The list of field names which may be considered "simple" and therefore
        treated as such, i.e. with basic getattr/setattr calls.  Note that this
        only applies to the local / target side, it has no effect on the
        upstream / foreign side.
        """
        return list(self.model_mapper.columns.keys())

    @property
    def supported_fields(self):
        """
        The list of field names which are supported in general by the importer.
        Note that this only applies to the local / target side, it has no
        effect on the upstream / foreign side.
        """
        return self.simple_fields

    @property
    def normalize_progress_message(self):
        return "Reading {} data from {}".format(self.model_name, self.handler.host_title)

    def setup(self):
        """
        Perform any setup necessary, e.g. cache lookups for existing data.
        """

    def teardown(self):
        """
        Perform any cleanup after import, if necessary.
        """

    def _setup(self, args, progress):
        self.now = datetime.datetime.utcnow()
        self.allow_create = self.allow_create and args.create
        self.allow_update = self.allow_update and args.update
        self.allow_delete = self.allow_delete and args.delete
        self.dry_run = args.dry_run
        self.args = args
        self.progress = progress
        self.setup()

    def import_data(self, args, progress=None):
        """
        Import some data!  This is the core body of logic for that, regardless
        of where data is coming from or where it's headed.  Note that this
        method handles deletions as well as adds/updates.
        """
        self._setup(args, progress)
        created = updated = deleted = []

        data = self.normalize_source_data()
        self.cached_instances = self.cache_instance_data(data)

        # Normalize source data set in order to prune duplicate keys.  This is
        # for the sake of sanity since duplicates typically lead to a ping-pong
        # effect, where a "clean" (change-less) import is impossible.
        unique = {}
        for record in data:
            key = self.get_key(record)
            if key in unique:
                log.warning("duplicate records detected from {} for key: {}".format(
                    self.handler.host_title, key))
            unique[key] = record
        data = []
        for key in sorted(unique):
            data.append(unique[key])

        if self.allow_create or self.allow_update:
            created, updated = self._import_create_update(data, args)

        if self.allow_delete:
            changes = len(created) + len(updated)
            if args.max_total and changes >= args.max_total:
                log.warning("max of {} total changes already reached; skipping deletions".format(args.max_total))
            else:
                deleted = self._import_delete(data, args, host_keys=set(unique), changes=changes)

        self.teardown()
        return created, updated, deleted

    def _import_create_update(self, data, args):
        """
        Import the given data; create and/or update records as needed and
        according to the args provided.
        """
        created = []
        updated = []
        count = len(data)
        if not count:
            return created, updated

        prog = None
        if self.progress:
            prog = self.progress("Importing {} data".format(self.model_name), count)

        keys_seen = set()
        for i, source_data in enumerate(data, 1):

            # Get what should be the unique key for the current 'host' data
            # record, but warn if we find it to be not unique.  Note that we
            # will still wind up importing both records however.
            key = self.get_key(source_data)
            if key in keys_seen:
                log.warning("duplicate records from {}:{} for key: {}".format(
                        self.__class__.__module__, self.__class__.__name__, key))
            else:
                keys_seen.add(key)

            # Fetch local instance, using key from host record.
            instance = self.get_instance(key)

            # If we have a local instance, but its data differs from host, update it.
            if instance and self.allow_update:
                instance_data = self.normalize_instance(instance)
                diffs = self.data_diffs(instance_data, source_data)
                if diffs:
                    log.debug("fields '{}' differed for local data: {}, host data: {}".format(
                            ','.join(diffs), instance_data, source_data))
                    instance = self.update_instance(instance, source_data, instance_data)
                    updated.append((instance, instance_data, source_data))
                    if args.max_update and len(updated) >= args.max_update:
                        log.warning("max of {} *updated* records has been reached; stopping now".format(args.max_update))
                        break
                    if args.max_total and (len(created) + len(updated)) >= args.max_total:
                        log.warning("max of {} *total changes* has been reached; stopping now".format(args.max_total))
                        break

            # If we did not yet have a local instance, create it using host data.
            elif not instance and self.allow_create:
                instance = self.create_instance(key, source_data)
                log.debug("created new {} {}: {}".format(self.model_name, key, instance))
                created.append((instance, source_data))
                if self.cached_instances is not None:
                    self.cached_instances[key] = {'instance': instance, 'data': self.normalize_instance(instance)}
                if args.max_create and len(created) >= args.max_create:
                    log.warning("max of {} *created* records has been reached; stopping now".format(args.max_create))
                    break
                if args.max_total and (len(created) + len(updated)) >= args.max_total:
                    log.warning("max of {} *total changes* has been reached; stopping now".format(args.max_total))
                    break

            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        return created, updated

    def get_deletion_keys(self):
        """
        Return a set of keys from the *local* data set, which are eligible for
        deletion.  By default this will be all keys from the local (cached)
        data set.
        """
        return set(self.cached_instances)

    def _import_delete(self, data, args, host_keys=None, changes=0):
        """
        Import deletions for the given data set.
        """
        if host_keys is None:
            host_keys = set([self.get_key(rec) for rec in data])

        deleted = []
        deleting = self.get_deletion_keys() - host_keys
        count = len(deleting)
        log.debug("found {} instances to delete".format(count))
        if count:

            prog = None
            if self.progress:
                prog = self.progress("Deleting {} data".format(self.model_name), count)

            for i, key in enumerate(sorted(deleting), 1):

                instance = self.cached_instances.pop(key)['instance']
                if self.delete_instance(instance):
                    deleted.append((instance, self.normalize_instance(instance)))

                    if args.max_delete and len(deleted) >= args.max_delete:
                        log.warning("max of {} *deleted* records has been reached; stopping now".format(args.max_delete))
                        break
                    if args.max_total and (changes + len(deleted)) >= args.max_total:
                        log.warning("max of {} *total changes* has been reached; stopping now".format(args.max_total))
                        break

                if prog:
                    prog.update(i)
            if prog:
                prog.destroy()

        return deleted

    def delete_instance(self, instance):
        """
        Process a deletion for the given instance.  The default implementation
        really does delete the instance from the local session, so you must
        override this if you need something else to happen.

        This method must return a boolean indicating whether or not the
        deletion was performed.  This implies for example that you may simply
        do nothing, and return ``False``, to effectively disable deletion
        altogether for an importer.
        """
        self.session.delete(instance)
        self.session.flush()
        self.session.expunge(instance)
        return True

    def get_source_data(self):
        """
        Return the "raw" (as-is, not normalized) data which is to be imported.
        This may be any sequence-like object, which has a ``len()`` value and
        responds to iteration etc.  The objects contained within it may be of
        any type, no assumptions are made there.  (That is the job of the
        :meth:`normalize_source_data()` method.)
        """
        return []

    def normalize_source_data(self):
        """
        Return a normalized version of the full set of source data.  Note that
        this calls :meth:`get_source_data()` to obtain the initial data set,
        and then normalizes each record.  the normalization process may filter
        out some records from the set, in which case the return value will be
        smaller than the original data set.
        """
        source_data = self.get_source_data()
        normalized = []
        count = len(source_data)
        if count == 0:
            return normalized
        prog = None
        if self.progress:
            prog = self.progress(self.normalize_progress_message, count)
        for i, data in enumerate(source_data, 1):
            data = self.normalize_source_record(data)
            if data:
                normalized.append(data)
            if prog:
                prog.update(i)
        if prog:
            prog.destroy()
        return normalized

    def get_key(self, data):
        """
        Return the key value for the given data record.
        """
        return tuple(data[k] for k in self.key)

    def int_(self, value):
        """
        Coerce ``value`` to an integer, or return ``None`` if that can't be
        done cleanly.
        """
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def prioritize_2(self, data, field):
        """
        Prioritize the data values for the pair of fields implied by the given
        fieldname.  I.e., if only one non-empty value is present, make sure
        it's in the first slot.
        """
        field2 = '{}_2'.format(field)
        if field in data and field2 in data:
            if data[field2] and not data[field]:
                data[field], data[field2] = data[field2], None

    def normalize_source_record(self, record):
        """
        Normalize a source data record.  Generally this is where the importer
        may massage the record in any way necessary, so that its values are
        more "native" and can be used for direct comparison with, and
        assignment to, the target model instance.

        Note that if you override this, your method must return the data to be
        imported.  If your method returns ``None`` then that particular record
        would be skipped and not imported.
        """
        return record

    def cache_model(self, model, **kwargs):
        """
        Convenience method which invokes :func:`rattail.db.cache.cache_model()`
        with the given model and keyword arguments.  It will provide the
        ``session`` and ``progress`` parameters by default, setting them to the
        importer's attributes of the same names.
        """
        session = kwargs.pop('session', self.session)
        kwargs.setdefault('progress', self.progress)
        return cache.cache_model(session, model, **kwargs)

    def cache_instance_data(self, data=None):
        """
        Cache all existing model instances as normalized data.
        """
        return cache.cache_model(self.session, self.model_class,
                                 key=self.get_cache_key,
                                 omit_duplicates=True,
                                 query_options=self.cache_query_options(),
                                 normalizer=self.normalize_cache_instance,
                                 progress=self.progress)

    def cache_query_options(self):
        """
        Return a list of options to apply to the cache query, if needed.
        """

    def get_cache_key(self, instance, normalized):
        """
        Get the primary model cache key for a given instance/data object.
        """
        return tuple(normalized['data'].get(k) for k in self.key)

    def normalize_cache_instance(self, instance):
        """
        Normalizer for cache data.  This adds the instance to the cache in
        addition to its normalized data.  This is so that if lots of updates
        are required, we don't we have to constantly fetch them.
        """
        return {'instance': instance, 'data': self.normalize_instance(instance)}

    def get_instance(self, key):
        """
        Must return the local object corresponding to the given key, or None.
        Default behavior here will be to check the cache if one is in effect,
        otherwise return the value from :meth:`get_single_instance()`.
        """
        if self.cached_instances is not None:
            data = self.cached_instances.get(key)
            return data['instance'] if data else None
        return self.get_single_instance(key)

    def get_single_instance(self, key):
        """
        Must return the local object corresponding to the given key, or None.
        This method should not consult the cache; that is handled within the
        :meth:`get_instance()` method.
        """
        query = self.session.query(self.model_class)
        for i, k in enumerate(self.key):
            query = query.filter(getattr(self.model_class, k) == key[i])

        try:
            return query.one()
        except NoResultFound:
            pass

    def normalize_instance(self, instance):
        """
        Normalize a model instance.
        """
        data = {}
        for field in self.simple_fields:
            if field in self.fields:
                data[field] = getattr(instance, field)
        return data

    def newval(self, data, field, value):
        """
        Assign a "new" field value to the given data record.  In other words
        don't try to be smart about not overwriting it if the existing data
        already matches etc.  However the main point of this is to skip fields
        which are not included in the current task.
        """
        if field in self.fields:
            data[field] = value

    def data_diffs(self, local_data, host_data):
        """
        Find all (relevant) fields which differ between the model and host data
        for a given record.
        """
        diffs = []
        for field in self.fields:
            if local_data[field] != host_data[field]:
                diffs.append(field)
        return diffs

    def create_instance(self, key, data):
        instance = self.new_instance(key)
        if instance:
            instance = self.update_instance(instance, data)
            if instance:
                self.session.add(instance)
                return instance

    def new_instance(self, key):
        """
        Return a new model instance to correspond to the given key.
        """
        instance = self.model_class()
        for i, k in enumerate(self.key):
            if hasattr(instance, k):
                setattr(instance, k, key[i])
        return instance

    def update_instance(self, instance, data, instance_data=None):
        """
        Update the given model instance with the given data.
        """
        for field in self.simple_fields:
            if field in self.fields:
                if not instance_data or instance_data[field] != data[field]:
                    setattr(instance, field, data[field])
        return instance


class QueryDataProxy(object):
    """
    Simple proxy to wrap a SQLAlchemy (or Django) query and make it sort of
    behave like a normal sequence, as much as needed to make an importer happy.
    """

    def __init__(self, query):
        self.query = query

    def __len__(self):
        return self.query.count()

    def __iter__(self):
        return iter(self.query)


class QueryImporter(Importer):
    """
    Base class for importers whose raw external data source is a SQLAlchemy (or
    Django) query.
    """

    def query(self):
        """
        Must return the primary query which will define the data set.
        """
        raise NotImplementedError

    def get_source_data(self, progress=None):
        return QueryDataProxy(self.query())


class SQLAlchemyImporter(QueryImporter):
    """
    Base class for importers whose external data source is a SQLAlchemy query.
    """
    host_session = None

    @property
    def host_model_class(self):
        """
        For default behavior, set this to a model class to be used in
        generating the host (source) data query.
        """
        raise NotImplementedError

    def query(self):
        """
        Must return the primary query which will define the data set.  Default
        behavior is to leverage :attr:`host_session` and generate a query for
        the class defined by :attr:`host_model_class`.
        """
        return self.host_session.query(self.host_model_class)


class BulkPostgreSQLImporter(Importer):
    """
    Base class for bulk data importers which target PostgreSQL on the local side.
    """

    def import_data(self, args, progress=None):
        self._setup(args, progress)
        self.open_data_buffers()
        data = self.normalize_source_data()
        created = self._import_create(data, args)
        self.teardown()
        return created

    def open_data_buffers(self):
        self.data_buffer = open(self.data_path, 'wb')

    def teardown(self):
        self.data_buffer.close()

    def _import_create(self, data, args):
        count = len(data)
        if not count:
            return 0
        created = count

        prog = None
        if self.progress:
            prog = self.progress("Importing {} data".format(self.model_name), count)

        for i, source_data in enumerate(data, 1):

            key = self.get_key(source_data)
            self.create_instance(key, source_data)
            if args.max_create and i >= args.max_create:
                log.warning("max of {} *created* records has been reached; stopping now".format(args.max_create))
                created = i
                break

            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        self.commit_create()
        return created

    def commit_create(self):
        log.info("copying {} data from buffer to PostgreSQL".format(self.model_name))
        self.seek_data_buffers()
        cursor = self.session.connection().connection.cursor()
        cursor.copy_from(self.data_buffer, self.model_table.name, columns=self.fields)
        log.debug("PostgreSQL data copy completed")

    def seek_data_buffers(self):
        self.data_buffer.close()
        self.data_buffer = open(self.data_path, 'rb')

    def create_instance(self, key, data):
        self.prep_data_for_postgres(data)
        self.data_buffer.write('{}\n'.format('\t'.join([data[field] for field in self.fields])))

    def prep_data_for_postgres(self, data):
        for key, value in data.iteritems():
            if value is None:
                value = '\\N'
            elif value is True:
                value = 't'
            elif value is False:
                value = 'f'
            elif isinstance(value, datetime.datetime):
                value = make_utc(value)
            elif isinstance(value, basestring):
                value = value.replace('\\', '\\\\')
                value = value.replace('\r\n', '\n')
                value = value.replace('\r', '\\r')
                value = value.replace('\n', '\\n')
            data[key] = unicode(value)
