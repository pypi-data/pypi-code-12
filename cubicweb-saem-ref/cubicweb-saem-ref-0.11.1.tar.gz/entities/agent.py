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
"""cubicweb-saem-ref entity's classes for Agent and its associated classes"""

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config

from cubes.oaipmh.entities import RelatedEntityOAISetSpec
from cubes.skos import rdfio
from cubes.skos.entities import AbstractRDFAdapter

from cubes.saem_ref.entities import oai


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


class Agent(AnyEntity):
    __regid__ = 'Agent'
    fetch_attrs, cw_fetch_order = fetch_config(('name', 'agent_kind'))

    @property
    def kind(self):
        """The kind of agent"""
        return self.agent_kind[0].name

    def has_role(self, role):
        """Return true if the agent has the archival role `role` else False"""
        return any(archival_role for archival_role in self.archival_role
                   if archival_role.name == role)

    @property
    def printable_kind(self):
        """The kind of agent, for display"""
        return self.agent_kind[0].printable_value('name')


def _fill_agent_rdf_mapping(reg, agent):
    reg.register_prefix('foaf', 'http://xmlns.com/foaf/0.1/')
    reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    foaf_kind = {'person': 'Person',
                 'authority': 'Organization',
                 'family': 'Group'}.get(agent.kind, 'Agent')
    reg.register_etype_equivalence('Agent', 'foaf:' + foaf_kind)
    # Standard metadata.
    reg.register_attribute_equivalence('Agent', 'name', 'foaf:name')
    # Additionnal metadata for Asalae export.
    reg.register_attribute_equivalence('Agent', 'ark', 'dc:identifier')


def _complete_agent_rdf_mapping(reg):
    reg.register_prefix('org', 'http://www.w3.org/ns/org#')
    reg.register_prefix('dct', 'http://purl.org/dc/terms/')
    reg.register_prefix('schema_org', 'http://schema.org/')
    reg.register_prefix('vcard', 'http://www.w3.org/2006/vcard/ns#')
    reg.register_attribute_equivalence('Agent', 'creation_date', 'dct:created')
    reg.register_attribute_equivalence('Agent', 'modification_date', 'dct:modified')
    reg.register_attribute_equivalence('Agent', 'start_date', 'schema_org:startDate')
    reg.register_attribute_equivalence('Agent', 'end_date', 'schema_org:endDate')
    reg.register_etype_equivalence('PostalAddress', 'vcard:Location')
    reg.register_attribute_equivalence('PostalAddress', 'street', 'vcard:street-address')
    reg.register_attribute_equivalence('PostalAddress', 'postalcode', 'vcard:postal-code')
    reg.register_attribute_equivalence('PostalAddress', 'city', 'vcard:locality')
    reg.register_attribute_equivalence('PostalAddress', 'country', 'vcard:country-name')
    reg.register_attribute_equivalence('PostalAddress', 'state', 'vcard:region')


class AgentRDFListAdapter(AbstractRDFAdapter):
    __regid__ = 'RDFList'
    __select__ = is_instance('Agent')

    def register_rdf_mapping(self, reg):
        _fill_agent_rdf_mapping(reg, self.entity)


class AgentRDFPrimaryAdapter(AgentRDFListAdapter):
    __regid__ = 'RDFPrimary'
    hierarchical_role = 'http://www.logilab.org/saem/hierarchical_role'
    association_role = 'http://www.logilab.org/saem/association_role'

    def register_rdf_mapping(self, reg):
        """RDF mapping for Agent entity type."""
        super(AgentRDFPrimaryAdapter, self).register_rdf_mapping(reg)
        _complete_agent_rdf_mapping(reg)
        reg.register_prefix('saem', 'http://www.logilab.org/saem/0#')
        reg.register_relation_equivalence('Agent', 'contact_point', 'Agent',
                                          'schema_org:contactPoint')
        reg.register_relation_equivalence('Agent', 'archival_agent', 'Agent',
                                          'saem:archivalAgent')

    def fill(self, graph):
        super(AgentRDFPrimaryAdapter, self).fill(graph)
        reg = self.registry
        generator = rdfio.RDFGraphGenerator(graph)
        # Export archival roles for the agent
        for archival_role in self.entity.archival_role:
            graph.add(graph.uri(self.entity.absolute_url()),
                      graph.uri(reg.normalize_uri('vcard:role')),
                      archival_role.name)
        # Export contact agent
        if self.entity.contact_point:
            contact_agent = self.entity.contact_point[0]
            # this is necessary to generate proper foaf:type for the contact agent, else it will
            # reuse the foaf:type of the exported agent
            contact_reg = rdfio.RDFRegistry()
            _fill_agent_rdf_mapping(contact_reg, contact_agent)
            _complete_agent_rdf_mapping(contact_reg)
            generator.add_entity(contact_agent, contact_reg)
        # Export addresses for the agent
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
            'reverse_chronological_predecessor': ('dct:isreplacedBy', 'dct: replaces'),
            'reverse_hierarchical_parent': ('org:organization', 'org:member'),
            'reverse_hierarchical_child': ('org:member', 'org:organization'),
        }
        # Export chronological relations
        for rtype_name, relation, related_agent in _iter_on_relations(
            self.entity, [('reverse_chronological_successor', 'chronological_predecessor'),
                          ('reverse_chronological_predecessor', 'chronological_successor')]):
            graph.add(graph.uri(related_agent.absolute_url()),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][1])),
                      graph.uri(self.entity.absolute_url()))
            graph.add(graph.uri(self.entity.absolute_url()),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][0])),
                      graph.uri(related_agent.absolute_url()))
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
        for rtype_name, relation, related_agent in relations:
            relation_url = relation.absolute_url()
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][0])),
                      graph.uri(self.entity.absolute_url()))
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri(rtype_to_properties[rtype_name][1])),
                      graph.uri(related_agent.absolute_url()))
            graph.add(graph.uri(relation_url),
                      graph.uri(reg.normalize_uri('org:role')),
                      graph.uri(role))
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
    """yield (rtype_name, relation, related_agent)

    `relation_descriptions` is a list of (rtype_name, reverse_rtype_name) regarding an
    Agent `entity`.
    """
    for rtype_name, reverse_rtype_name, in relation_descriptions:
        for relation in getattr(entity, rtype_name):
            for related_agent in getattr(relation, reverse_rtype_name):
                yield rtype_name, relation, related_agent


class AgentOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for Agent entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('Agent')
    metadata_view = 'primary.rdf'

    @classmethod
    def set_definition(cls):
        specifier = oai.PublicETypeOAISetSpec(
            'Agent', identifier_attribute=cls.identifier_attribute)
        specifier['role'] = RelatedEntityOAISetSpec(
            'archival_role', 'ArchivalRole', 'name',
            description=u'An agent with {0} archival role')
        specifier['kind'] = RelatedEntityOAISetSpec(
            'agent_kind', 'AgentKind', 'name',
            description=u'An agent of kind {0}',
            exclude=['unknown-agent-kind'])
        return specifier


class AgentKind(AnyEntity):
    __regid__ = 'AgentKind'
    fetch_attrs, cw_fetch_order = fetch_config(('name',))


class ArchivalRole(AnyEntity):
    __regid__ = 'AgentKind'
    fetch_attrs, cw_fetch_order = fetch_config(('name',))


class ChronologicalRelation(AnyEntity):
    __regid__ = 'ChronologicalRelation'

    def dc_description(self):
        if self.description:
            return self.description


class EACResourceRelation(AnyEntity):
    __regid__ = 'EACResourceRelation'

    @property
    def agent(self):
        return self.resource_relation_agent[0]

    @property
    def resource(self):
        return self.resource_relation_resource[0]

    def dc_title(self):
        agent_title = self.agent.dc_title()
        if self.agent_role:
            agent_title += u' (%s)' % self.printable_value('agent_role')
        resource_title = self.resource.dc_title()
        if self.resource_role:
            resource_title += u' (%s)' % self.printable_value('resource_role')
        return (self._cw._('Relation from %(from)s to %(to)s ') %
                {'from': agent_title,
                 'to': resource_title})


class SameAsMixIn(object):
    """Mix-in class for entity types supporting vocabulary_source and equivalent_concept relations
    """

    @property
    def scheme(self):
        return self.vocabulary_source and self.vocabulary_source[0] or None

    @property
    def concept(self):
        return self.equivalent_concept and self.equivalent_concept[0] or None


class AgentPlace(SameAsMixIn, AnyEntity):
    __regid__ = 'AgentPlace'


class AgentFunction(SameAsMixIn, AnyEntity):
    __regid__ = 'AgentFunction'


class Mandate(SameAsMixIn, AnyEntity):
    __regid__ = 'Mandate'


class LegalStatus(SameAsMixIn, AnyEntity):
    __regid__ = 'LegalStatus'


class Occupation(SameAsMixIn, AnyEntity):
    __regid__ = 'Occupation'
