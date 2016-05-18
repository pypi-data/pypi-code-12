# coding: utf-8
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
from lxml import etree

from mock import MagicMock, patch

from cubicweb import Binary
from cubicweb.devtools.testlib import CubicWebTC

from cubes.skos.rdfio import RDFLibRDFGraph

import testutils


class AgentExportTC(CubicWebTC, testutils.XmlTestMixin):
    """Functional test case for agent exports"""

    @patch('cubes.saem_ref.hooks.datetime')
    def setup_database(self, mock_dt):
        mock_dt.utcnow.return_value = datetime.datetime(2016, 2, 1)
        with self.admin_access.client_cnx() as cnx:
            work_address2 = cnx.create_entity('PostalAddress', street=u"1 av. de l'europe",
                                              postalcode=u'31400', city=u'Toulouse')
            work_address3 = cnx.create_entity('PostalAddress', street=u'104 bd L.-A. Blanqui',
                                              postalcode=u'75013', city=u'Paris')
            home_address = cnx.create_entity('PostalAddress', street=u'Place du Capitole',
                                             postalcode=u'31000', city=u'Toulouse')
            agent1 = testutils.agent(cnx, u'Alice', archival_roles=['deposit'])
            agent2 = testutils.agent(cnx, u'Super Service', kind=u'authority',
                                     archival_roles=['archival'],
                                     contact_point=agent1,
                                     reverse_archival_agent=agent1)
            cnx.create_entity('AgentPlace', role=u'work', place_agent=agent2,
                              place_address=work_address2)
            agent3 = testutils.agent(cnx, u'Charlie', ark=u'1234',
                                     archival_roles=['archival', 'control'])
            cnx.create_entity('AgentPlace', role=u'work', place_agent=agent3,
                              place_address=work_address3)
            cnx.create_entity('AgentPlace', role=u'home', place_agent=agent3,
                              place_address=home_address)
            cnx.create_entity('ChronologicalRelation',
                              chronological_predecessor=agent2,
                              xml_wrap=Binary('<plip>plop</plip>'),
                              chronological_successor=agent3)
            logilab_uri = cnx.create_entity('ExternalUri', uri=u'http://www.logilab.fr')
            cnx.create_entity('EACResourceRelation',
                              resource_relation_resource=logilab_uri,
                              resource_relation_agent=agent3,
                              xml_wrap=Binary('<pif><paf>pouf</paf></pif>'))
            gironde = testutils.agent(cnx, u'Gironde. Conseil général', kind=u'authority',
                                      archival_roles=['archival', 'control'],
                                      ark=u'FRAD033_EAC_00001',
                                      start_date=datetime.date(1800, 1, 1),
                                      end_date=datetime.date(2099, 1, 1),
                                      isni=u'22330001300016')
            delphine = testutils.agent(cnx, u'Delphine Jamet')
            adm_dir = testutils.agent(cnx, u"Gironde. Conseil général. Direction de "
                                      u"l'administration et de la sécurité juridique",
                                      kind=u'unknown-agent-kind')
            cg32 = testutils.agent(cnx, u'CG32', kind=u'unknown-agent-kind')
            trash = testutils.agent(cnx, u'Trash', kind=u'unknown-agent-kind')
            place_uri = cnx.create_entity('ExternalUri',
                                          uri=u'http://catalogue.bnf.fr/ark:/12148/cb152418385',
                                          cwuri=u'http://catalogue.bnf.fr/ark:/12148/cb152418385')
            agent_x = cnx.create_entity('ExternalUri', uri=u'agent-x', cwuri=u'agent-x')
            social_action_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200',
                cwuri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200')
            environment_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074',
                cwuri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074')
            resource_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N',
                cwuri=u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N')
            meeting_uri = cnx.create_entity(
                'ExternalUri', uri=u'http://example.org/meeting',
                cwuri=u'http://example.org/meeting')
            cnx.create_entity('EACSource', title=u'1. Ouvrages imprimés...',
                              description=u'des bouquins', source_agent=gironde)
            cnx.create_entity('EACSource', title=u'Site des Archives départementales de la Gironde',
                              url=u'http://archives.gironde.fr', source_agent=gironde,
                              xml_wrap=Binary('<some>thing</some>'))
            cnx.create_entity('Activity', type=u'create',
                              start=datetime.datetime(2013, 4, 24, 5, 34, 41),
                              end=datetime.datetime(2013, 4, 24, 5, 34, 41),
                              description=u'bla bla bla', generated=gironde)
            cnx.create_entity('Activity', type=u'modify', associated_with=delphine,
                              start=datetime.datetime(2015, 1, 15, 7, 16, 33),
                              end=datetime.datetime(2015, 1, 15, 7, 16, 33),
                              generated=gironde)
            gironde_address = cnx.create_entity('PostalAddress',
                                                street=u'1 Esplanade Charles de Gaulle',
                                                postalcode=u'33074', city=u'Bordeaux Cedex')
            cnx.create_entity('AgentPlace', role=u'siege', name=u'Bordeaux (Gironde, France)',
                              place_agent=gironde, place_address=gironde_address,
                              equivalent_concept=place_uri)
            cnx.create_entity('AgentPlace', role=u'domicile', name=u'Toulouse (France)',
                              place_agent=gironde)
            cnx.create_entity('AgentPlace', role=u'dodo', name=u'Lit',
                              place_agent=gironde)
            cnx.create_entity('LegalStatus', term=u'Collectivité territoriale',
                              start_date=datetime.date(1234, 1, 1),
                              end_date=datetime.date(3000, 1, 1),
                              description=u'Description du statut',
                              legal_status_agent=gironde,
                              has_citation=[cnx.create_entity('Citation', note=u"legal foo")])
            cnx.create_entity('Mandate', term=u'1. Constitutions françaises',
                              description=u'Description du mandat',
                              mandate_agent=gironde)
            cnx.create_entity(
                'History',
                text=(
                    u"<p>La loi du 22 décembre 1789, en divisant ...</p>\n"
                    u"<p>L'inspecteur Canardo</p>"
                ),
                text_format=u"text/html",
                history_agent=gironde,
                has_citation=[
                    cnx.create_entity('Citation', uri=(
                        u"http://www.assemblee-nationale.fr/histoire/images-decentralisation/"
                        u"decentralisation/loi-du-22-decembre-1789-.pdf"
                    )),
                    cnx.create_entity('Citation',
                                      uri=u"http://pifgadget", note=u"Voir aussi pifgadget"),
                ],
            )
            cnx.create_entity('GeneralContext',
                              content=u'<p>sous une pluie battante</p>',
                              content_format=u'text/html',
                              has_citation=cnx.create_entity(
                                  'Citation', uri=u'http://meteoplouf.net'),
                              general_context_of=gironde)
            cnx.create_entity('Structure',
                              description=u'Pour accomplir ses missions ...',
                              structure_agent=gironde)
            cnx.create_entity('AgentFunction',
                              description=u'Quatre grands domaines de compétence...',
                              function_agent=gironde)
            cnx.create_entity('AgentFunction', name=u'action sociale',
                              description=u'1. Solidarité\nblablabla.',
                              function_agent=gironde, equivalent_concept=social_action_uri)
            cnx.create_entity('AgentFunction', name=u'environnement',
                              function_agent=gironde, equivalent_concept=environment_uri)
            cnx.create_entity('Occupation', term=u'Réunioniste',
                              description=u'Organisation des réunions ...',
                              start_date=datetime.date(1987, 1, 1),
                              end_date=datetime.date(2099, 1, 1),
                              occupation_agent=gironde, equivalent_concept=meeting_uri)
            cnx.create_entity('HierarchicalRelation', hierarchical_parent=adm_dir,
                              hierarchical_child=gironde, description=u'Coucou',
                              start_date=datetime.date(2008, 1, 1),
                              end_date=datetime.date(2099, 1, 1))
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=cg32,
                              chronological_successor=gironde)
            cnx.create_entity('ChronologicalRelation', chronological_predecessor=gironde,
                              chronological_successor=trash)
            cnx.create_entity('AssociationRelation', association_from=gironde,
                              association_to=agent_x)
            cnx.create_entity('EACResourceRelation', agent_role=u'creatorOf',
                              resource_role=u"Fonds d'archives",
                              start_date=datetime.date(1673, 1, 1),
                              end_date=datetime.date(1963, 1, 1),
                              resource_relation_resource=resource_uri,
                              resource_relation_agent=gironde)
            cnx.commit()
            gironde.cw_adapt_to('IWorkflowable').fire_transition('publish')
            cnx.commit()
            self.agent1_eid = agent1.eid
            self.agent2_eid = agent2.eid
            self.agent3_eid = agent3.eid
            self.gironde_eid = gironde.eid
            self.adm_dir_eid = adm_dir.eid
            self.cg32_eid = cg32.eid
            self.trash_eid = trash.eid
            self.agent_x_eid = agent_x.eid
            self.work_address2_eid = work_address2.eid
            self.work_address3_eid = work_address3.eid
            self.home_address_eid = home_address.eid

    def assertItemsIn(self, items, container):
        """Check that elements of `items` are in `container`."""
        for item in items:
            self.assertIn(item, container)

    def assertItemsNotIn(self, items, container):
        """Check that elements of `items` are not in `container`."""
        for item in items:
            self.assertNotIn(item, container)

    def test_agent_rdf_primary_adapter(self):
        role_uri = u'http://www.w3.org/2006/vcard/ns#role'
        type_uri = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        person_uri = u'http://xmlns.com/foaf/0.1/Person'
        org_uri = u'http://xmlns.com/foaf/0.1/Organization'
        contact_uri = u'http://schema.org/contactPoint'
        name_uri = u'http://xmlns.com/foaf/0.1/name'
        address_uri = u'http://www.w3.org/2006/vcard/ns#hasAddress'
        archival_agent_uri = u'http://www.logilab.org/saem/0#archivalAgent'
        replaced_uri = u'http://purl.org/dc/terms/isReplacedBy'
        replaces_uri = u'http://purl.org/dc/terms/replaces'
        with self.admin_access.client_cnx() as cnx:
            agent1 = cnx.entity_from_eid(self.agent1_eid)
            agent2 = cnx.entity_from_eid(self.agent2_eid)
            agent3 = cnx.entity_from_eid(self.agent3_eid)
            gironde = cnx.entity_from_eid(self.gironde_eid)
            gironde = cnx.entity_from_eid(self.gironde_eid)
            agent_x = cnx.entity_from_eid(self.agent_x_eid)
            adm_dir = cnx.entity_from_eid(self.adm_dir_eid)
            work_address2 = cnx.entity_from_eid(self.work_address2_eid)
            work_address3 = cnx.entity_from_eid(self.work_address3_eid)
            home_address = cnx.entity_from_eid(self.home_address_eid)
            # No archival role / no address
            triples = self._retrieve_triples(agent1, 'RDFPrimary')
            self.assertItemsIn([(agent1.absolute_url(), type_uri, person_uri),
                                (agent1.absolute_url(), name_uri, u'Alice')],
                               triples)
            self.assertItemsIn([(agent1.absolute_url(), archival_agent_uri, agent2.absolute_url())],
                               triples)
            self.assertItemsNotIn(
                [(agent1.absolute_url(), role_uri, u'archival'),
                 (agent1.absolute_url(), role_uri, u'control'),
                 (agent1.absolute_url(), address_uri, work_address2.absolute_url()),
                 (agent1.absolute_url(), address_uri, work_address3.absolute_url()),
                 (agent1.absolute_url(), address_uri, home_address.absolute_url()),
                 (agent2.absolute_url(), name_uri, u'Super Service'),
                 ], triples)
            # One archival role / one address
            triples = self._retrieve_triples(agent2, 'RDFPrimary')
            self.assertItemsIn([(agent2.absolute_url(), type_uri, org_uri),
                                (agent2.absolute_url(), name_uri, u'Super Service'),
                                (agent2.absolute_url(), role_uri, u'archival'),
                                (agent2.absolute_url(), address_uri,
                                 work_address2.absolute_url()),
                                (work_address2.absolute_url(), role_uri, 'work')],
                               triples)
            # agent1 in the graph as contact point of agent2
            self.assertItemsIn([(agent2.absolute_url(), contact_uri, agent1.absolute_url()),
                                (agent1.absolute_url(), type_uri, person_uri),
                                (agent1.absolute_url(), name_uri, u'Alice')],
                               triples)
            self.assertItemsNotIn(
                [(agent2.absolute_url(), role_uri, u'control'),
                 (agent2.absolute_url(), address_uri, work_address3.absolute_url()),
                 (work_address3.absolute_url(), role_uri, 'work'),
                 (agent2.absolute_url(), address_uri, home_address.absolute_url())],
                triples)
            # Two archival roles
            triples = self._retrieve_triples(agent3, 'RDFPrimary')
            self.assertItemsIn(
                [(agent3.absolute_url(), type_uri, person_uri),
                 (agent3.absolute_url(), name_uri, u'Charlie'),
                 (agent3.absolute_url(), role_uri, u'archival'),
                 (agent3.absolute_url(), role_uri, u'control'),
                 (agent3.absolute_url(), address_uri, work_address3.absolute_url()),
                 (work_address3.absolute_url(), role_uri, 'work'),
                 (agent3.absolute_url(), address_uri, home_address.absolute_url()),
                 (home_address.absolute_url(), role_uri, 'home')],
                triples)
            self.assertNotIn(
                (agent3.absolute_url(), address_uri, work_address2.absolute_url()),
                triples)
            # agent1 replaced by agent2 and agent2 replaced by agent3
            self.assertItemsIn(
                [(agent2.absolute_url(), replaced_uri, agent3.absolute_url()),
                 (agent3.absolute_url(), replaces_uri, agent2.absolute_url())],
                triples)
            # hierarchical relations: adm_dir parent of gironde
            triples = self._retrieve_triples(gironde, 'RDFPrimary')
            relation = adm_dir.reverse_hierarchical_parent[0]
            relation_url = relation.absolute_url()
            interval_resource = relation_url + '#timeInterval'
            expected_hierarchical_relations = [
                (relation_url, u'http://www.w3.org/ns/org#organization', adm_dir.absolute_url()),
                (relation_url, u'http://www.w3.org/ns/org#member', gironde.absolute_url()),
                (relation_url, u'http://www.w3.org/ns/org#role',
                 u'http://www.logilab.org/saem/hierarchical_role'),
                (relation_url, u'http://www.w3.org/ns/org#memberDuring', interval_resource),
                (interval_resource, u'http://schema.org/startDate', datetime.date(2008, 1, 1)),
                (interval_resource, u'http://schema.org/endDate', datetime.date(2099, 1, 1)),
            ]
            self.assertItemsIn(expected_hierarchical_relations, triples)
            triples = self._retrieve_triples(adm_dir, 'RDFPrimary')
            self.assertItemsIn(expected_hierarchical_relations, triples)
            # association relations: agent_x and gironde are associated
            triples = self._retrieve_triples(gironde, 'RDFPrimary')
            relation = gironde.reverse_association_from[0]
            relation_url = relation.absolute_url()
            interval_resource = relation_url + '#timeInterval'
            expected_association_relations = [
                (relation_url, u'http://www.w3.org/ns/org#organization', gironde.absolute_url()),
                (relation_url, u'http://www.w3.org/ns/org#member', agent_x.absolute_url()),
                (relation_url, u'http://www.w3.org/ns/org#member', gironde.absolute_url()),
                (relation_url, u'http://www.w3.org/ns/org#organization', agent_x.absolute_url()),
                (relation_url, u'http://www.w3.org/ns/org#role',
                 u'http://www.logilab.org/saem/association_role'),
                (relation_url, u'http://www.w3.org/ns/org#memberDuring', interval_resource),
            ]
            self.assertItemsIn(expected_association_relations, triples)

    def _retrieve_triples(self, agent, adapter_name):
        graph = RDFLibRDFGraph()
        agent.cw_adapt_to(adapter_name).fill(graph)
        return list(graph.triples())

    def test_agent_eac_export_simple(self):
        # Given an agent (created in setup_database), export it to EAC-CPF
        with self.admin_access.client_cnx() as cnx:
            agent3 = cnx.entity_from_eid(self.agent3_eid)
            agent2 = cnx.entity_from_eid(self.agent2_eid)
            agent2.absolute_url = MagicMock(return_value=u'http://www.example.org/agent2')
            agent3_eac = agent3.cw_adapt_to('EAC-CPF').dump()
        # Then check that output XML is as expected
        with open(self.datapath('EAC/agent3_export.xml')) as f:
            expected_eac = f.read().replace("@@@EID_GOES_HERE@@@", str(self.agent3_eid))
        self.assertXmlEqual(agent3_eac, expected_eac)
        self.assertXmlValid(agent3_eac, self.datapath('cpf.xsd'))

    def test_agent_eac_export_full(self):
        with self.admin_access.client_cnx() as cnx:
            for eid, absolute_url in (
                (self.adm_dir_eid, u'http://www.example.org/adm_dir'),
                (self.cg32_eid, u'http://www.example.org/cg32'),
                (self.trash_eid, u"/dev/null"),
                (self.agent_x_eid, u'http://www.example.org/agent_x'),
            ):
                cnx.entity_from_eid(eid).absolute_url = MagicMock(return_value=absolute_url)
            gironde = cnx.entity_from_eid(self.gironde_eid)
            gironde_eac = gironde.cw_adapt_to('EAC-CPF').dump()
        with open(self.datapath('EAC/FRAD033_EAC_00001_simplified_export.xml')) as f:
            expected_eac = f.read().replace("@@@EID_GOES_HERE@@@", str(self.gironde_eid))
        self.assertXmlEqual(gironde_eac, expected_eac)
        self.assertXmlValid(gironde_eac, self.datapath('cpf.xsd'))


class EACExportTC(CubicWebTC):
    """Unit tests for EAC-CPF exports."""

    def test_richstring_plain(self):
        with self.admin_access.cnx() as cnx:
            alice = testutils.agent(cnx, u'Alice')
            desc = u'ding'
            mandate = cnx.create_entity(
                'Mandate', term=u'ding-girl',
                description=desc, description_format=u'text/plain',
                mandate_agent=alice)
            cnx.commit()
            serializer = alice.cw_adapt_to('EAC-CPF')
            tag, = serializer._eac_richstring_paragraph_elements(
                mandate, 'description')
        self.assertEqual(tag.tag, 'p')
        self.assertEqual(tag.text, desc)

    def test_richstring_html_simple(self):
        with self.admin_access.cnx() as cnx:
            alice = testutils.agent(cnx, u'Alice')
            desc = u'<span>ding</span>'
            mandate = cnx.create_entity(
                'Mandate', term=u'ding-girl',
                description=desc, description_format=u'text/html',
                mandate_agent=alice)
            cnx.commit()
            serializer = alice.cw_adapt_to('EAC-CPF')
            tag, = serializer._eac_richstring_paragraph_elements(
                mandate, 'description')
        self.assertEqual(tag.tag, 'span')
        self.assertIn(desc, etree.tostring(tag))

    def test_richstring_html_multiple_elements(self):
        with self.admin_access.cnx() as cnx:
            alice = testutils.agent(cnx, u'Alice')
            desc = [u'<h1>she <i>rules!</i></h1>', u'<a href="1">pif</a>']
            mandate = cnx.create_entity(
                'Mandate', term=u'chairgirl',
                description=u''.join(desc), description_format=u'text/html',
                mandate_agent=alice)
            cnx.commit()
            serializer = alice.cw_adapt_to('EAC-CPF')
            h1, a = serializer._eac_richstring_paragraph_elements(
                mandate, 'description')
        self.assertEqual(h1.tag, 'h1')
        self.assertEqual(a.tag, 'a')
        self.assertIn(etree.tostring(h1), desc[0])
        self.assertIn(etree.tostring(a), desc[1])

    def test_richstring_markdown(self):
        with self.admin_access.cnx() as cnx:
            alice = testutils.agent(cnx, u'Alice')
            desc = u'[pif](http://gadget.com) is *red*'
            desc_html = (
                u'<a href="http://gadget.com">pif</a> '
                u'is <em>red</em>'
            )
            mandate = cnx.create_entity(
                'Mandate', term=u'w',
                description=desc, description_format=u'text/markdown',
                mandate_agent=alice)
            cnx.commit()
            serializer = alice.cw_adapt_to('EAC-CPF')
            tag, = serializer._eac_richstring_paragraph_elements(
                mandate, 'description')
        self.assertEqual(tag.tag, 'p')
        self.assertIn(desc_html, etree.tostring(tag))

    def test_richstring_rest(self):
        with self.admin_access.cnx() as cnx:
            alice = testutils.agent(cnx, u'Alice')
            desc = u'`pif <http://gadget.com>`_ is *red*'
            desc_html = (
                u'<a class="reference" href="http://gadget.com">pif</a> '
                u'is <em>red</em>'
            )
            mandate = cnx.create_entity(
                'Mandate', term=u'w',
                description=desc, description_format=u'text/rest',
                mandate_agent=alice)
            cnx.commit()
            serializer = alice.cw_adapt_to('EAC-CPF')
            ptag, = serializer._eac_richstring_paragraph_elements(
                mandate, 'description')
        self.assertEqual(ptag.tag, 'p')
        self.assertIn(desc_html, etree.tostring(ptag))

    def test_richstring_empty(self):
        def check(agent):
            serializer = agent.cw_adapt_to('EAC-CPF')
            res = serializer._eac_richstring_paragraph_elements(
                mandate, 'description')
            self.assertEqual(res, [])

        with self.admin_access.cnx() as cnx:
            alice = testutils.agent(cnx, u'Alice')
            mandate = cnx.create_entity(
                'Mandate', term=u'w',
                description=None,
                mandate_agent=alice)
            cnx.commit()
            check(alice)
        with self.admin_access.cnx() as cnx:
            cnx.execute(
                'SET X description_format "text/rest" WHERE X is Mandate')
            cnx.commit()
            agent = cnx.find('Agent', name=u'Alice').one()
            check(agent)


if __name__ == '__main__':
    import unittest
    unittest.main()
