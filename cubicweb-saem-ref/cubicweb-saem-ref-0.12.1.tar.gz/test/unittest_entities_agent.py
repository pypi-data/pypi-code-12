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
"""Tests for agent entities"""

import datetime

from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import RDFLibRDFGraph, RDFRegistry

import testutils


class RDFExportTC(testutils.XmlTestMixin, CubicWebTC):
    """Test case for RDF export"""

    def setUp(self):
        super(RDFExportTC, self).setUp()
        self.reg = RDFRegistry()
        self.reg.register_prefix('rdf', 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        self.reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
        self.reg.register_prefix('dcterms', 'http://purl.org/dc/terms/')
        self.reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
        self.reg.register_prefix('lglb', 'http://www.logilab.org/saem/0#')
        self.reg.register_prefix('org', 'http://www.w3.org/ns/org#')
        self.reg.register_prefix('schema', 'http://schema.org/')
        self.reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')

    def _rdf_triples(self, entity, adapter_name='RDFPrimary'):
        graph = RDFLibRDFGraph()
        entity.cw_adapt_to(adapter_name).fill(graph)
        return list(graph.triples())

    def assertItemsIn(self, items, container):
        """Check that elements of `items` are in `container`."""
        for item in items:
            self.assertIn(item, container)

    def assertItemsNotIn(self, items, container):
        """Check that elements of `items` are not in `container`."""
        for item in items:
            self.assertNotIn(item, container)

    def uri(self, s):
        return self.reg.normalize_uri(s)

    def test_organization_unit(self):
        with self.admin_access.client_cnx() as cnx:
            agent = testutils.agent(cnx, u'John Doe')
            ou = testutils.organization_unit(cnx, u'Acme Inc.',
                                             archival_roles=['deposit', 'control'],
                                             contact_point=agent)
            triples = self._rdf_triples(ou)
            self.assertItemsIn([
                (ou.absolute_url(), self.uri('rdf:type'), self.uri('foaf:Organization')),
                (ou.absolute_url(), self.uri('foaf:name'), u'Acme Inc.'),
                (ou.absolute_url(), self.uri('dc:identifier'), ou.ark),
                (ou.absolute_url(), self.uri('vcard:role'), u'deposit'),
                (ou.absolute_url(), self.uri('vcard:role'), u'control'),
                (ou.absolute_url(), self.uri('schema:contactPoint'), agent.absolute_url()),
                (agent.absolute_url(), self.uri('rdf:type'), self.uri('foaf:Person')),
                (agent.absolute_url(), self.uri('foaf:name'), u'John Doe'),
                (agent.absolute_url(), self.uri('dc:identifier'), agent.ark),
            ], triples)

    def test_agent(self):
        with self.admin_access.client_cnx() as cnx:
            agent = testutils.agent(cnx, u'Roger Rabbit')
            triples = self._rdf_triples(agent)
            self.assertItemsIn([
                (agent.absolute_url(), self.uri('rdf:type'), self.uri('foaf:Person')),
                (agent.absolute_url(), self.uri('foaf:name'), u'Roger Rabbit'),
                (agent.absolute_url(), self.uri('dc:identifier'), agent.ark),
            ], triples)

    def test_authority_record_foaf_type(self):
        with self.admin_access.client_cnx() as cnx:
            for kind, foaf_kind in ((u'authority', 'Organization'),
                                    (u'person', 'Person'),
                                    (u'family', 'Group')):
                record = testutils.authority_record(cnx, u'Acme', kind=kind)
                triples = self._rdf_triples(record)
                self.assertItemsIn([
                    (record.absolute_url(), self.uri('rdf:type'), self.uri('foaf:' + foaf_kind)),
                    (record.absolute_url(), self.uri('foaf:name'), u'Acme'),
                    (record.absolute_url(), self.uri('dc:identifier'), record.ark),
                ], triples)

    def test_authority_record_places(self):
        with self.admin_access.client_cnx() as cnx:
            record = testutils.authority_record(cnx, u'Acme Inc. Authority')
            work_address = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                             postalcode=u'31400', city=u'Toulouse')
            cnx.create_entity('AgentPlace', role=u'work', place_agent=record,
                              place_address=work_address)
            home_address = cnx.create_entity('PostalAddress', street=u"Place du Capitole",
                                             postalcode=u'31000', city=u'Toulouse')
            cnx.create_entity('AgentPlace', role=u'home', place_agent=record,
                              place_address=home_address)
            triples = self._rdf_triples(record)
            self.assertItemsIn([
                (record.absolute_url(), self.uri('vcard:hasAddress'), work_address.absolute_url()),
                (work_address.absolute_url(), self.uri('vcard:role'), 'work'),
                (record.absolute_url(), self.uri('vcard:hasAddress'), home_address.absolute_url()),
                (home_address.absolute_url(), self.uri('vcard:role'), 'home'),
            ], triples)

    def test_authority_record_with_chronological_relation(self):
        with self.admin_access.client_cnx() as cnx:
            record1 = testutils.authority_record(cnx, u'Acme Inc. Authority')
            record2 = testutils.authority_record(cnx, u'Acme2 Inc. Authority')
            record3 = testutils.authority_record(cnx, u'Acme3 Inc. Authority')
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=record1,
                              chronological_successor=record2)
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=record2,
                              chronological_successor=record3)
            triples = self._rdf_triples(record2)
            self.assertItemsIn([
                (record2.absolute_url(), self.uri('dcterms:isReplacedBy'), record3.absolute_url()),
                (record2.absolute_url(), self.uri('dcterms:replaces'), record1.absolute_url()),
            ], triples)

    def test_authority_record_with_hierarchical_relation_rdf_export(self):
        with self.admin_access.client_cnx() as cnx:
            record1 = testutils.authority_record(cnx, u'Acme Inc. Authority')
            record2 = testutils.authority_record(cnx, u'Acme Group. Authority')
            cnx.create_entity('HierarchicalRelation',
                              hierarchical_parent=record2,
                              hierarchical_child=record1,
                              start_date=datetime.date(2008, 1, 1),
                              end_date=datetime.date(2099, 1, 1))
            relation_url = record1.reverse_hierarchical_child[0].absolute_url()
            time_interval_url = relation_url + '#timeInterval'
            expected_hierarchical_relations = [
                (relation_url, self.uri('org:organization'), record2.absolute_url()),
                (relation_url, self.uri('org:member'), record1.absolute_url()),
                (relation_url, self.uri('org:role'),
                 'http://www.logilab.org/saem/hierarchical_role'),
                (relation_url, self.uri('org:memberDuring'), time_interval_url),
                (time_interval_url, self.uri('schema:startDate'), datetime.date(2008, 1, 1)),
                (time_interval_url, self.uri('schema:endDate'), datetime.date(2099, 1, 1)),
            ]
            triples = self._rdf_triples(record1)
            self.assertItemsIn(expected_hierarchical_relations, triples)
            triples = self._rdf_triples(record2)
            self.assertItemsIn(expected_hierarchical_relations, triples)

    def test_authority_record_with_associative_relation_rdf_export(self):
        with self.admin_access.client_cnx() as cnx:
            record1 = testutils.authority_record(cnx, u'Acme Inc. Authority')
            record2 = cnx.create_entity('ExternalUri', uri=u'agent2', cwuri=u'agent2')
            cnx.create_entity('AssociationRelation',
                              association_from=record1,
                              association_to=record2)
            relation_url = record1.reverse_association_from[0].absolute_url()
            triples = self._rdf_triples(record1)
            self.assertItemsIn([
                (relation_url, self.uri('org:organization'), record1.absolute_url()),
                (relation_url, self.uri('org:member'), record2.absolute_url()),
                (relation_url, self.uri('org:member'), record1.absolute_url()),
                (relation_url, self.uri('org:organization'), record2.absolute_url()),
                (relation_url, self.uri('org:role'),
                 u'http://www.logilab.org/saem/association_role'),
            ], triples)


if __name__ == '__main__':
    import unittest
    unittest.main()
