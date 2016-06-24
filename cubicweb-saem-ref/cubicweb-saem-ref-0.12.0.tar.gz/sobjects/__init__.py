# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref server objects"""

from itertools import imap

from cubicweb import ValidationError
from cubicweb.predicates import match_user_groups
from cubicweb.server import Service
from cubicweb.dataimport import RQLObjectStore
from cubicweb.dataimport.importer import ExtEntitiesImporter, cwuri2eid

from cubes.skos import to_unicode

from cubes.saem_ref import user_has_naa
from cubes.saem_ref.dataimport import eac


class EACImportService(Service):
    """Service to import an AuthorityRecord from an EAC XML file"""
    __regid__ = 'saem_ref.eac-import'
    __select__ = match_user_groups('managers', 'users') & user_has_naa()

    def call(self, stream, import_log, naa=None, **kwargs):
        authority = self._cw.user.authority[0]
        if naa is None:
            naa = authority.ark_naa[0]
        store = RQLObjectStore(self._cw)
        source = self._cw.repo.system_source
        # only consider the system source for EAC related entity types
        extid2eid = cwuri2eid(self._cw, eac.ETYPES_ORDER_HINT, source_eid=source.eid)
        # though concepts may come from any source
        extid2eid.update(cwuri2eid(self._cw, ('Concept',)))
        importer = ExtEntitiesImporter(self._cw.vreg.schema, store,
                                       import_log=import_log,
                                       extid2eid=extid2eid,
                                       etypes_order_hint=eac.ETYPES_ORDER_HINT,
                                       **kwargs)
        extimporter = eac.EACCPFImporter(stream, import_log, self._cw._)
        extentities = extimporter.external_entities()
        extentities = (ee for ee in extentities
                       if not (ee.etype == 'ExternalUri' and ee.extid in extid2eid))

        def handle_agent_kind(extentities):
            """Create agent kind when necessary and remove them from the entity stream, allowing to
            set cwuri properly without attempt to update.
            """
            for extentity in extentities:
                if extentity.etype == 'AgentKind':
                    if extentity.extid not in extid2eid:
                        name = next(iter(extentity.values['name']))
                        kind = self._cw.create_entity('AgentKind', name=name,
                                                      cwuri=unicode(extentity.extid))
                        extid2eid[extentity.extid] = kind.eid
                else:
                    yield extentity
        extentities = handle_agent_kind(extentities)

        def set_authority_or_naa(extentity):
            """insert function to set parent authority in the ext-entities stream"""
            if extentity.etype == 'AuthorityRecord':
                extentity.values['ark_naa'] = set([naa.cwuri])
            elif extentity.etype == 'Agent':
                extentity.values['authority'] = set([authority.cwuri])
            return extentity

        extentities = imap(set_authority_or_naa, extentities)
        extid2eid[naa.cwuri] = naa.eid
        extid2eid[authority.cwuri] = authority.eid

        try:
            importer.import_entities(extentities)
        except Exception as exc:
            self._cw.rollback()
            import_log.record_fatal(to_unicode(exc))
            raise
        else:
            try:
                self._cw.commit()
            except ValidationError as exc:
                import_log.record_error('validation error: ' + to_unicode(exc))
                raise
            else:
                import_log.record_info('%s entities created' % len(importer.created))
                import_log.record_info('%s entities updated' % len(importer.updated))
        if extimporter.record is not None:
            extid = extimporter.record.extid
            record_eid = importer.extid2eid[extid]
        else:
            record_eid = None
        msg = self._cw._('element {0}, line {1} not parsed')
        for tagname, sourceline in extimporter.not_visited():
            import_log.record_warning(msg.format(tagname, sourceline))
        return importer.created, importer.updated, record_eid


class AllocateArk(Service):
    """Service to allocate an ark identifier"""
    __regid__ = 'saem_ref.attribute-ark'
    __select__ = match_user_groups('managers', 'users') & user_has_naa()

    def call(self):
        naa = self._cw.user.naa
        generator = self._cw.vreg['adapters'].select('IARKGenerator', self._cw,
                                                     naa_what=naa.what)
        return generator.generate_ark()
