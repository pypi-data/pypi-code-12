# copyright 2014-2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-datacat server objects"""

import hashlib

from cubicweb.server.sources import datafeed
from cubicweb.dataimport import NoHookRQLObjectStore, MetaGenerator
from cubicweb.dataimport.importer import (ExtEntity, ExtEntitiesImporter,
                                          HTMLImportLog)


def compute_sha1hex(value):
    """Return the SHA1 hex digest of `value`."""
    return unicode(hashlib.sha1(value).hexdigest())


class ResourceFeedParser(datafeed.DataFeedParser):
    """Fetch files and apply validation and transformation processes before
    attaching them to their Dataset as Resources.
    """
    __regid__ = 'datacat.resourcefeed-parser'

    def importer(self, url, extid2eid):
        """Return an ExtEntity importer."""
        cnx = self._cw
        schema = cnx.vreg.schema
        # XXX Using NoHookRQLObjectStore because RQLObjectStore does not
        # support setting cw_source relation.
        metagenerator = MetaGenerator(cnx, source=self.source)
        store = NoHookRQLObjectStore(cnx, metagenerator)
        import_log = HTMLImportLog(url)
        return ExtEntitiesImporter(schema, store, import_log=import_log,
                                   extid2eid=extid2eid)

    def extid2eid(self):
        qs = 'Any H,X WHERE X data_sha1hex H, X cw_source S, S eid %(s)s'
        args = {'s': self.source.eid}
        return dict(self._cw.execute(qs, args))

    def process(self, url, raise_on_error=False):
        """Build a File entity from data fetched from url"""
        stream = self.retrieve_url(url)
        data = stream.read()
        sha1hex = compute_sha1hex(data)
        extid2eid = self.extid2eid()
        extentity = ExtEntity('File', sha1hex)
        if extentity.extid not in extid2eid:
            # Only set `values` when the entity does not already exist
            # (otherwise the importer will consider the entity for update
            # which is not what we want).
            extentity.values.update(
                {'data_name': set([url.split('/')[-1]]),
                 'data_sha1hex': set([sha1hex]),
                 'data': set([data])}
            )
        importer = self.importer(url, extid2eid)
        importer.import_entities([extentity])
        created, updated = importer.created, importer.updated
        self.debug('data import for %s completed: created %d entities, updated %s entities',
                   url, len(created), len(updated))
        entity = None
        if created:
            assert not updated, 'unexpected update of entities {0}'.format(updated)
            assert len(created) == 1, created
            entity = self._cw.entity_from_eid(created.pop())
            self.stats['created'].add(entity.eid)
        if updated:
            assert not created, 'unexpected creation of entities {0}'.format(created)
            assert len(updated) == 1, updated
            entity = self._cw.entity_from_eid(updated.pop())
            self.stats['updated'].add(entity.eid)
        if entity is not None:
            # Ensure imported entity as a cw_source, otherwise re-import would
            # not work.
            assert entity.cw_source
            self.process_data(entity)

    def process_data(self, entity):
        """Launch validation and transformation scripts of all related
        ResourceFeed entities.
        """
        cwsource = self._cw.entity_from_eid(self.source.eid)
        data_format = None
        for resourcefeed in cwsource.reverse_resource_feed_source:
            if data_format:
                # XXX Better do this in a schema constraint on
                # `resource_feed_source` relation.
                if resourcefeed.data_format != data_format:
                    raise ValueError('MIME types of resource feeds attached to '
                                     'CWSource #%d mismatch' % cwsource.eid)
            else:
                data_format = resourcefeed.data_format
                entity.cw_set(data_format=resourcefeed.data_format,
                              file_distribution=resourcefeed.resourcefeed_distribution)
            # Link imported file to distribution.
            self._cw.execute(
                'SET F file_distribution D WHERE F eid %(f)s, R resourcefeed_distribution D, '
                'R eid %(r)s, NOT EXISTS(F file_distribution D)',
                {'f': entity.eid, 'r': resourcefeed.eid})
            # Run the validation script for imported file.
            vprocess = None
            if resourcefeed.validation_script:
                vscript = resourcefeed.validation_script[0]
                vprocess = self._cw.create_entity('DataValidationProcess',
                                                  process_for_resourcefeed=resourcefeed,
                                                  validation_script=vscript,
                                                  process_input_file=entity)
                self.debug('created validation process #%d for file #%d',
                           vprocess.eid, entity.eid)
            if resourcefeed.transformation_script:
                tseq = resourcefeed.transformation_script[0].transformation_sequence
                tprocess = self._cw.create_entity('DataTransformationProcess',
                                                  process_for_resourcefeed=resourcefeed,
                                                  transformation_sequence=tseq,
                                                  process_input_file=entity,
                                                  process_depends_on=vprocess)
                self.debug('created transformation process #%d for file #%d',
                           tprocess.eid, entity.eid)
