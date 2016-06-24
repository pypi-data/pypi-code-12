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
"""Adapters to export content to RDF"""

from cubicweb.predicates import is_instance
from cubes.skos import rdfio
from cubes.skos.entities import AbstractRDFAdapter


def _register_agent_prov_mapping(reg):  # XXX move to the prov cube
    """Register RDF mapping for PROV-O entity types related to Agent.
    """
    reg.register_prefix('prov', 'http://www.w3.org/ns/prov#')
    # reg.register_etype_equivalence('Agent', 'prov:Agent')
    reg.register_etype_equivalence('Activity', 'prov:Activity')
    reg.register_attribute_equivalence('Activity', 'type', 'prov:type')
    reg.register_attribute_equivalence('Activity', 'description', 'prov:label')
    reg.register_attribute_equivalence('Activity', 'start', 'prov:startedAtTime')
    reg.register_attribute_equivalence('Activity', 'end', 'prov:endedAtTime')
    reg.register_relation_equivalence('Activity', 'associated_with', 'Agent',
                                      'prov:wasAssociatedWith')
    reg.register_relation_equivalence('Activity', 'generated', 'Agent', 'prov:generated')
    reg.register_relation_equivalence('Activity', 'used', 'Agent', 'prov:used')


def _base_rdf_mapping(reg, etype, foaf_kind):
    reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
    reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    reg.register_etype_equivalence(etype, 'foaf:' + foaf_kind)
    # Standard metadata.
    reg.register_attribute_equivalence(etype, 'name', 'foaf:name')
    # Additionnal metadata for Asalae export.
    reg.register_attribute_equivalence(etype, 'ark', 'dc:identifier')


def _complete_agent_rdf_mapping(reg, etype):
    reg.register_prefix('dct', 'http://purl.org/dc/terms/')
    reg.register_prefix('schema_org', 'http://schema.org/')
    reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
    reg.register_attribute_equivalence(etype, 'creation_date', 'dct:created')
    reg.register_attribute_equivalence(etype, 'modification_date', 'dct:modified')


def _complete_authority_record_rdf_mapping(reg, etype):
    _complete_agent_rdf_mapping(reg, etype)
    reg.register_attribute_equivalence(etype, 'start_date', 'schema_org:startDate')
    reg.register_attribute_equivalence(etype, 'end_date', 'schema_org:endDate')
    reg.register_etype_equivalence('PostalAddress', 'vcard:Location')
    reg.register_attribute_equivalence('PostalAddress', 'street', 'vcard:street-address')
    reg.register_attribute_equivalence('PostalAddress', 'postalcode', 'vcard:postal-code')
    reg.register_attribute_equivalence('PostalAddress', 'city', 'vcard:locality')
    reg.register_attribute_equivalence('PostalAddress', 'country', 'vcard:country-name')
    reg.register_attribute_equivalence('PostalAddress', 'state', 'vcard:region')


class AgentRDFListAdapter(AbstractRDFAdapter):
    __regid__ = 'RDFList'
    __select__ = is_instance('Agent', 'OrganizationUnit')

    def register_rdf_mapping(self, reg):
        foaf_kind = {
            'Agent': 'Person',
            'OrganizationUnit': 'Organization',
        }[self.entity.cw_etype]
        _base_rdf_mapping(reg, self.entity.cw_etype, foaf_kind)


class AgentRDFPrimaryAdapter(AgentRDFListAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('Agent')

    def register_rdf_mapping(self, reg):
        super(AgentRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg, self.entity.cw_etype)


class OrganizationUnitRDFPrimaryAdapter(AgentRDFListAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('OrganizationUnit')

    def register_rdf_mapping(self, reg):
        super(OrganizationUnitRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg, self.entity.cw_etype)
        reg.register_relation_equivalence(
            'OrganizationUnit', 'contact_point', 'Agent',
            'schema_org:contactPoint')

    def fill(self, graph):
        super(OrganizationUnitRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        # Export archival roles for the agent
        for archival_role in self.entity.archival_role:
            graph.add(graph.uri(self.entity.absolute_url()),
                      graph.uri(reg.normalize_uri('vcard:role')),
                      archival_role.name)
        # Export contact agent
        if self.entity.contact_point:
            contact_agent = self.entity.contact_point[0]
            contact_agent.cw_adapt_to('RDFPrimary').fill(graph)


class AuthorityRecordRDFPrimaryAdapter(AbstractRDFAdapter):
    __regid__ = 'RDFPrimary'
    __select__ = is_instance('AuthorityRecord')

    hierarchical_role = 'http://www.logilab.org/saem/hierarchical_role'
    association_role = 'http://www.logilab.org/saem/association_role'

    def register_rdf_mapping(self, reg):
        """RDF mapping for AuthorityRecord entity type."""
        reg.register_prefix('org', 'http://www.w3.org/ns/org#')
        foaf_kind = {'person': 'Person',
                     'authority': 'Organization',
                     'family': 'Group'}.get(self.entity.kind, 'Person')
        _base_rdf_mapping(reg, 'AuthorityRecord', foaf_kind)
        _complete_authority_record_rdf_mapping(reg, self.entity.cw_etype)

    def fill(self, graph):
        super(AuthorityRecordRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        generator = rdfio.RDFGraphGenerator(graph)
        # Export addresses
        for place in self.entity.reverse_place_agent:
            for address in place.place_address:
                graph.add(graph.uri(self.entity.absolute_url()),
                          graph.uri(reg.normalize_uri('vcard:hasAddress')),
                          graph.uri(address.absolute_url()))
                if place.role:
                    graph.add(graph.uri(address.absolute_url()),
                              graph.uri(reg.normalize_uri('vcard:role')),
                              place.role)
                generator.add_entity(address, reg)
        # rtype name: (subj property, obj property)
        rtype_to_properties = {
            'reverse_chronological_successor': ('dct:replaces', 'dct:isReplacedBy'),
            'reverse_chronological_predecessor': ('dct:isReplacedBy', 'dct:replaces'),
            'reverse_hierarchical_parent': ('org:organization', 'org:member'),
            'reverse_hierarchical_child': ('org:member', 'org:organization'),
        }
        # Export chronological relations
        relations_generator = _iter_on_relations(
            self.entity,
            [('reverse_chronological_successor', 'chronological_predecessor'),
             ('reverse_chronological_predecessor', 'chronological_successor')])
        for rtype_name, relation, related_record in relations_generator:
            to_predicate, from_predicate = rtype_to_properties[rtype_name]
            graph.add(graph.uri(related_record.absolute_url()),
                      graph.uri(reg.normalize_uri(from_predicate)),
                      graph.uri(self.entity.absolute_url()))
            graph.add(graph.uri(self.entity.absolute_url()),
                      graph.uri(reg.normalize_uri(to_predicate)),
                      graph.uri(related_record.absolute_url()))
        # Export hierarchical relations
        relations_generator = _iter_on_relations(
            self.entity,
            [('reverse_hierarchical_parent', 'hierarchical_child'),
             ('reverse_hierarchical_child', 'hierarchical_parent')])
        self._add_membership_to_graph(graph, self.hierarchical_role, relations_generator,
                                      rtype_to_properties)
        # Export association relations
        relations_generator = _iter_on_relations(
            self.entity,
            [('reverse_association_from', 'association_to'),
             ('reverse_association_to', 'association_from')])
        # As this is an association relation, it makes no sense to have an agent being the
        # organization rather than the other one. That is why we "duplicate" Membership
        # properties: each agent will be both known as a member and an organization.
        relations = list(relations_generator)
        self._add_membership_to_graph(
            graph, self.association_role, relations,
            {'reverse_association_from': ('org:organization', 'org:member'),
             'reverse_association_to': ('org:member', 'org:organization')})
        self._add_membership_to_graph(
            graph, self.association_role, relations,
            {'reverse_association_from': ('org:member', 'org:organization'),
             'reverse_association_to': ('org:organization', 'org:member')})

    def _add_membership_to_graph(self, graph, role, relations, rtype_to_properties):
        reg = self.registry
        for rtype_name, relation, related_record in relations:
            relation_url = relation.absolute_url()
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][0])),
                      graph.uri(self.entity.absolute_url()))
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][1])),
                      graph.uri(related_record.absolute_url()))
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri('org:role')),
                      graph.uri(role))
            if relation.start_date or relation.end_date:
                interval_resource = reg.normalize_uri(relation_url + '#timeInterval')
                graph.add(graph.uri(relation_url),
                          graph.uri(reg.normalize_uri('org:memberDuring')),
                          graph.uri(interval_resource))
            if relation.start_date:
                graph.add(graph.uri(interval_resource),
                          graph.uri(reg.normalize_uri('schema_org:startDate')),
                          relation.start_date)
            if relation.end_date:
                graph.add(graph.uri(interval_resource),
                          graph.uri(reg.normalize_uri('schema_org:endDate')),
                          relation.end_date)


def _iter_on_relations(entity, relation_descriptions):
    """yield (rtype_name, relation, related_entity)

    `relation_descriptions` is a list of (rtype_name, reverse_rtype_name)
    """
    for rtype_name, reverse_rtype_name in relation_descriptions:
        for relation in getattr(entity, rtype_name):
            for related_entity in getattr(relation, reverse_rtype_name):
                yield rtype_name, relation, related_entity
