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
"""SKOS import overrides"""

import sys

from cubes.skos import sobjects as skos

from cubes.saem_ref.backports.stores import MetadataGenerator, NoHookRQLObjectStore
from cubes.saem_ref.backports.massive_store import MassiveObjectStore
from cubes.saem_ref.hooks import set_ark_and_cwuri


def _store(cnx, **kwargs):
    metagen = SAEMMetadataGenerator(cnx, **kwargs)
    # XXX detect if import is started through source-sync, because the massive store isn't usable
    # when other connections are active on the database
    if 'source-sync' in sys.argv and cnx.repo.system_source.dbdriver == 'postgres':
        return MassiveObjectStore(cnx, metagen=metagen, eids_seq_range=1000)
    else:
        return NoHookRQLObjectStore(cnx, metagen=metagen)


class SAEMMetadataGenerator(MetadataGenerator):
    """SAEM specific metadata generator, necessary when no hooks are activated (e.g. skos import) to
    handle ARK generation and setting of the initial state.
    """

    def __init__(self, cnx, baseurl=None, source=None, naa_what=None):
        super(SAEMMetadataGenerator, self).__init__(cnx, baseurl, source)
        if naa_what is None and source is not None:
            source_entity = cnx.find('CWSource', eid=source.eid).one()
            if source_entity.reverse_through_cw_source:
                skos_source = source_entity.reverse_through_cw_source[0]
                if skos_source.ark_naa:
                    naa_what = skos_source.ark_naa[0].what
        self.naa_what = naa_what

    def etype_rels(self, etype):
        etype_rels = super(SAEMMetadataGenerator, self).etype_rels(etype)
        if etype == 'ConceptScheme':
            etype_rels.append('in_state')
        return etype_rels

    def gen_in_state(self, etype):
        wf_state = self._cnx.execute('Any S WHERE ET default_workflow WF, ET name %(etype)s, '
                                     'WF initial_state S', {'etype': etype}).one()
        return wf_state.eid

    def entity_attrs(self, etype):
        entity_attrs = super(SAEMMetadataGenerator, self).entity_attrs(etype)
        if etype in ('ConceptScheme', 'Concept'):
            entity_attrs.insert(0, 'ark')  # insert before cwuri
        return entity_attrs

    def gen_ark(self, etype, eid, attrs):
        """ARK generation callback"""
        set_ark_and_cwuri(self._cnx, eid, etype, attrs, naa_what=self.naa_what)
        # returning value, even if set by the function, is necessary due to the meta generator
        # implementation
        return attrs['ark']


class RDFSKOSImportService(skos.RDFSKOSImportService):
    """service overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, stream, import_log, **kwargs):
        return super(RDFSKOSImportService, self)._do_import(stream, import_log,
                                                            store=_store(self._cw), **kwargs)


class LCSVSKOSImportService(skos.LCSVSKOSImportService):
    """service overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, stream, import_log, **kwargs):
        scheme = self._cw.find('ConceptScheme', cwuri=kwargs['scheme_uri']).one()
        naa_what = scheme.cw_adapt_to('IArkNAALocator').naa_what()
        store = _store(self._cw, naa_what=naa_what)
        return super(LCSVSKOSImportService, self)._do_import(stream, import_log,
                                                             store=store, **kwargs)


class SKOSParser(skos.SKOSParser):
    """parser overriden from skos cube to provide functionnalities handled in saem_ref's hooks"""

    def _do_import(self, url, raise_on_error):
        return super(SKOSParser, self)._do_import(url, raise_on_error=raise_on_error,
                                                  store=_store(self._cw, source=self.source))


def registration_callback(vreg):
    vreg.register_and_replace(RDFSKOSImportService, skos.RDFSKOSImportService)
    vreg.register_and_replace(LCSVSKOSImportService, skos.LCSVSKOSImportService)
    vreg.register_and_replace(SKOSParser, skos.SKOSParser)
