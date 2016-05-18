# -*- coding: utf-8 -*-
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref entity's classes for exporting agents to eac"""
from functools import wraps

from lxml import etree

from logilab.common.date import ustrftime
from cubicweb.predicates import is_instance

from cubes.saem_ref import (cwuri_url, eactype_mapping, eacaddress_mapping,
                            eacmaintenancetype_mapping)
from cubes.saem_ref.entities import AbstractXmlAdapter


def add_object_xml_wrap(func):
    """Add an objectXMLWrap sub-element to the element returned by `func`."""
    def wrapper(self, entity, *args, **kwargs):
        elem = func(self, entity, *args, **kwargs)
        if entity.xml_wrap is not None:
            objectXMLWrap = self.element('objectXMLWrap', parent=elem)
            objectXMLWrap.append(etree.parse(entity.xml_wrap).getroot())
        return elem
    return wraps(func)(wrapper)


def add_descriptive_note(func):
    @wraps(func)
    def wrapper(self, entity, *args, **kwargs):
        element = func(self, entity, *args, **kwargs)
        if element is not None and entity.description:
            self.element('descriptiveNote', parent=element).extend(
                self._eac_richstring_paragraph_elements(entity, "description"))
        return element
    return wrapper


def add_citation(func):
    @wraps(func)
    def wrapper(self, entity, *args, **kwargs):
        element = func(self, entity, *args, **kwargs)
        for citation in entity.has_citation:
            attrs = {'xlink:type': 'simple'}
            if citation.uri:
                attrs['xlink:href'] = citation.uri
            self.element('citation', parent=element, attributes=attrs, text=citation.note)
        return element
    return wrapper


class AgentEACAdapter(AbstractXmlAdapter):
    __regid__ = 'EAC-CPF'
    __select__ = is_instance('Agent')

    namespaces = {
        None: u'urn:isbn:1-931666-33-4',
        u'xsi': u'http://www.w3.org/2001/XMLSchema-instance',
        u'xlink': u'http://www.w3.org/1999/xlink',
    }
    datetime_fmt = '%Y-%m-%dT%H:%M:%S'

    @property
    def file_name(self):
        """Return a file name for the dump."""
        if self.entity.ark:
            name = self.entity.ark.replace("/", "_")
        else:
            name = unicode(self.entity.eid)
        return u'EAC_{0}.xml'.format(name)

    def dump(self):
        """Return an XML string representing the given agent using the EAC-CPF schema."""
        # Keep related activities since they are used multiple times
        self.activities = sorted(self.entity.reverse_generated, key=lambda x: x.start, reverse=True)
        # Root element
        eac_cpf_elt = self.element('eac-cpf', attributes={
            'xsi:schemaLocation': ('urn:isbn:1-931666-33-4 '
                                   'http://eac.staatsbibliothek-berlin.de/schema/cpf.xsd')
        })
        # Top elements: control & cpfDescription
        self.control_element(eac_cpf_elt)
        self.cpfdescription_element(eac_cpf_elt)
        tree = etree.ElementTree(eac_cpf_elt)
        return etree.tostring(tree, xml_declaration=True, encoding='utf-8', pretty_print=True)

    def control_element(self, eac_cpf_elt):
        control_elt = self.element('control', parent=eac_cpf_elt)
        self.element('recordId', parent=control_elt, text=unicode(self.entity.eid))
        self.maintenance_status_element(control_elt)
        self.publication_status_element(control_elt)
        self.maintenance_agency_element(control_elt)
        self.language_declaration_element(control_elt)
        self.maintenance_history_element(control_elt)
        self.sources_element(control_elt)

    def cpfdescription_element(self, eac_cpf_elt):
        cpfdescription_elt = self.element('cpfDescription', parent=eac_cpf_elt)
        self.identity_element(cpfdescription_elt)
        self.description_element(cpfdescription_elt)
        self.relations_element(cpfdescription_elt)

    def maintenance_status_element(self, control_elt):
        if any(activity.type == 'modify' for activity in self.activities):
            status = 'revised'
        else:
            status = 'new'
        self.element('maintenanceStatus', parent=control_elt, text=status)

    def publication_status_element(self, control_elt):
        status = {'draft': 'inProcess', 'published': 'approved'}.get(
            self.entity.cw_adapt_to('IWorkflowable').state, 'inProcess')
        self.element('publicationStatus', parent=control_elt, text=status)

    def maintenance_agency_element(self, control_elt):
        agency_elt = self.element('maintenanceAgency', parent=control_elt)
        self.element('agencyName', parent=agency_elt)

    def language_declaration_element(self, control_elt):
        lang_decl_elt = self.element('languageDeclaration', parent=control_elt)
        self.element('language', parent=lang_decl_elt,
                     attributes={'languageCode': 'fre'}, text=u'français')
        self.element('script', parent=lang_decl_elt, attributes={'scriptCode': 'Latn'},
                     text='latin')

    def maintenance_history_element(self, control_elt):
        history_elt = self.element('maintenanceHistory', parent=control_elt)
        for activity in self.activities:
            self.maintenance_event_element(activity, history_elt)

    def sources_element(self, control_elt):
        sources_elt = self.element('sources')
        for eac_source in self.entity.reverse_source_agent:
            sources_elt.append(self.source_element(eac_source))
        if len(sources_elt):
            control_elt.append(sources_elt)

    def identity_element(self, cpfdescription_elt):
        identity_elt = self.element('identity', parent=cpfdescription_elt)
        self._elt_text_from_attr('entityId', self.entity, 'isni', parent=identity_elt)
        type_mapping = dict((v, k) for k, v in eactype_mapping.items())
        eac_type = type_mapping.get(self.entity.kind)
        self.element('entityType', parent=identity_elt, text=eac_type)
        name_entry = self.element('nameEntry', parent=identity_elt)  # XXX: authorizedForm
        self.element('part', parent=name_entry, text=self.entity.name)

    def description_element(self, cpfdescription_elt):
        agent = self.entity
        description_elt = self.element('description', parent=cpfdescription_elt)
        self.exist_dates_element(description_elt)
        for relation, group_tagname, get_element in [
            ('reverse_place_agent', 'places', self.place_element),
            ('reverse_function_agent', 'functions', self.function_element),
            ('reverse_legal_status_agent', 'legalStatuses', self.legal_status_element),
            ('reverse_occupation_agent', 'occupations', self.occupation_element),
            ('reverse_mandate_agent', 'mandates', self.mandate_element),
        ]:
            relateds = getattr(agent, relation)
            if relateds:
                group_elt = self.element(group_tagname, parent=description_elt)
                for related in relateds:
                    group_elt.append(get_element(related))
        for structure in agent.reverse_structure_agent:
            structure_elt = self.structure_element(structure)
            if len(structure_elt):
                description_elt.append(structure_elt)
        for generalcontext in agent.reverse_general_context_of:
            generalcontext_elt = self.generalcontext_element(generalcontext)
            if len(generalcontext_elt):
                description_elt.append(generalcontext_elt)
        for history in agent.reverse_history_agent:
            bioghist_elt = self.bioghist_element(history)
            if len(bioghist_elt):
                description_elt.append(bioghist_elt)

    def relations_element(self, cpfdescription_elt):
        relations_elt = self.element('relations')
        for rtype, rel_rtype, eac_rtype in [
            ('reverse_hierarchical_child', 'hierarchical_parent', 'hierarchical-parent'),
            ('reverse_hierarchical_parent', 'hierarchical_child', 'hierarchical-child'),
            ('reverse_chronological_successor', 'chronological_predecessor', 'temporal-earlier'),
            ('reverse_chronological_predecessor', 'chronological_successor', 'temporal-later'),
            ('reverse_association_to', 'association_from', 'associative'),
            ('reverse_association_from', 'association_to', 'associative')
        ]:
            for relation in getattr(self.entity, rtype):
                relations_elt.append(
                    self.cpfrelation_element(relation, rel_rtype, eac_rtype))
        for resource_relation in self.entity.reverse_resource_relation_agent:
            relations_elt.append(
                self.resource_relation_element(resource_relation))
        if len(relations_elt):
            cpfdescription_elt.append(relations_elt)

    def maintenance_event_element(self, activity, history_elt):
        event_elt = self.element('maintenanceEvent', parent=history_elt)
        type_mapping = dict((v, k) for k, v in eacmaintenancetype_mapping.items())
        activity_type = type_mapping.get(activity.type, 'created')
        self.element('eventType', parent=event_elt, text=activity_type)
        self.element('eventDateTime', parent=event_elt,
                     attributes={'standardDateTime': ustrftime(activity.start,
                                                               fmt=self.datetime_fmt)},
                     text=ustrftime(activity.start, fmt=self.datetime_fmt))
        ass_agent = activity.associated_with
        if ass_agent:
            self.agent_element(ass_agent[0], event_elt)
        else:  # These tags must be present, even if name is empty
            agent_type_elt = self.element('agentType', text='machine')
            event_elt.append(agent_type_elt)
            event_elt.append(self.element('agent'))
        self._elt_text_from_attr('eventDescription', activity, 'description', parent=event_elt)

    @add_descriptive_note
    @add_object_xml_wrap
    def source_element(self, eac_source):
        url = eac_source.url
        attributes = {'xlink:href': url, 'xlink:type': 'simple'} if url else None
        source_elt = self.element('source', attributes=attributes)
        self.element('sourceEntry', parent=source_elt, text=eac_source.title)
        return source_elt

    def exist_dates_element(self, description_elt):
        date_range = self._eac_date_range_xml_elt(self.entity.start_date, self.entity.end_date)
        if date_range is not None:
            exist_dates = self.element('existDates', parent=description_elt)
            exist_dates.append(date_range)

    @add_citation
    def place_element(self, place):
        place_elt = self.element('place')
        for attr, eac_name in [('role', 'placeRole'), ('name', 'placeEntry')]:
            eac_elt = self._elt_text_from_attr(eac_name, place, attr, parent=place_elt)
            if eac_elt is not None and eac_name == 'placeEntry' and place.equivalent_concept:
                eac_elt.attrib['vocabularySource'] = cwuri_url(place.equivalent_concept[0])
        for address in place.place_address:
            self.address_element(address, place_elt)
        return place_elt

    @add_descriptive_note
    @add_citation
    def function_element(self, function):
        function_elt = self.element('function')
        term_elt = self._elt_text_from_attr('term', function, 'name', parent=function_elt)
        if term_elt is not None and function.equivalent_concept:
            term_elt.attrib['vocabularySource'] = cwuri_url(function.equivalent_concept[0])
        return function_elt

    @add_descriptive_note
    @add_citation
    def legal_status_element(self, legal_status):
        legal_status_elt = self.element('legalStatus')
        self._elt_text_from_attr('term', legal_status, 'term', parent=legal_status_elt)
        return legal_status_elt

    @add_descriptive_note
    @add_citation
    def occupation_element(self, occupation):
        occupation_elt = self.element('occupation')
        term_elt = self._elt_text_from_attr('term', occupation, 'term', parent=occupation_elt)
        if term_elt is not None and occupation.equivalent_concept:
            term_elt.attrib['vocabularySource'] = cwuri_url(occupation.equivalent_concept[0])
        self._eac_date_range_xml_elt(occupation.start_date, occupation.end_date,
                                     parent=occupation_elt)
        return occupation_elt

    @add_descriptive_note
    @add_citation
    def mandate_element(self, mandate):
        mandate_elt = self.element('mandate')
        term_elt = self._elt_text_from_attr('term', mandate, 'term', parent=mandate_elt)
        if term_elt is not None and mandate.equivalent_concept:
            term_elt.attrib['vocabularySource'] = cwuri_url(mandate.equivalent_concept[0])
        return mandate_elt

    def structure_element(self, structure):
        structure_elt = self.element('structureOrGenealogy')
        if structure.description:
            structure_elt.extend(self._eac_richstring_paragraph_elements(structure, "description"))
        return structure_elt

    @add_citation
    def generalcontext_element(self, context):
        context_elt = self.element('generalContext')
        if context.content:
            context_elt.extend(self._eac_richstring_paragraph_elements(context, 'content'))
        return context_elt

    @add_citation
    def bioghist_element(self, history):
        bioghist_elt = self.element('biogHist')
        if history.text:
            bioghist_elt.extend(self._eac_richstring_paragraph_elements(history, "text"))
        return bioghist_elt

    @add_descriptive_note
    @add_object_xml_wrap
    def cpfrelation_element(self, relation, cw_rtype, eac_rtype):
        related = relation.related(cw_rtype).one()  # exactly one target (schema)
        relation_elt = self.element('cpfRelation',
                                    attributes={'cpfRelationType': eac_rtype,
                                                'xlink:href': related.absolute_url(),
                                                'xlink:type': 'simple'})
        if related.cw_etype != 'ExternalUri':
            self.element('relationEntry', parent=relation_elt, text=related.name)
        self._eac_date_range_xml_elt(getattr(relation, 'start_date', None),
                                     getattr(relation, 'end_date', None),
                                     parent=relation_elt)
        return relation_elt

    @add_object_xml_wrap
    def resource_relation_element(self, resource_relation):
        resource = resource_relation.resource_relation_resource[0]
        attrs = {
            'xlink:href': resource.uri,
            'xlink:type': 'simple',
        }
        if resource_relation.resource_role:
            attrs['xlink:role'] = resource_relation.resource_role
        if resource_relation.agent_role:
            attrs['resourceRelationType'] = resource_relation.agent_role
        res_rel_elt = self.element('resourceRelation', attributes=attrs)
        self._eac_date_range_xml_elt(resource_relation.start_date, resource_relation.end_date,
                                     parent=res_rel_elt)
        return res_rel_elt

    def agent_element(self, agent, maintenance_event_elt):
        self.element('agentType', maintenance_event_elt, text='human')
        self.element('agent', maintenance_event_elt, text=agent.name)

    def address_element(self, address, place_elt):
        address_elt = self.element('address', parent=place_elt)
        for eac_name, attr in eacaddress_mapping:
            self._elt_text_from_attr('addressLine', address, attr,
                                     attributes={'localType': eac_name}, parent=address_elt)

    #
    # helper methods for lxml
    #

    def _elt_text_from_attr(self, tag_name, entity, attr_name, parent=None, attributes=None):
        """Return an lxml `Element` whose text is the value of the given attribute on the given
        entity.

        If this element is not empty and if ``parent`` is not ``None``, the element will also be
        inserted in the parent XML element.

        If ``attributes`` is not ``None``, these attributes will be added to the returned element.

        Return ``None`` if element is empty.
        """
        value = getattr(entity, attr_name)
        if value is not None:
            elt = self.element(tag_name, parent=parent, attributes=attributes, text=value)
            return elt

    def _eac_date_range_xml_elt(self, start_date, end_date, parent=None):
        """Return an EAC lxml ``'dateRange'`` ``Element`` with the given boundaries."""
        if not start_date and not end_date:
            return
        date_range = self.element('dateRange', parent=parent)
        for dt, eac_name in [(start_date, 'fromDate'), (end_date, 'toDate')]:
            if not dt:
                continue
            self.element(eac_name, parent=date_range,
                         attributes={'standardDate': dt.isoformat()}, text=dt.isoformat())
        return date_range

    def _eac_richstring_paragraph_elements(self, entity, attr_name):
        fmt = getattr(entity, attr_name + "_format")
        if fmt == "text/plain":
            value = getattr(entity, attr_name)
            if not value:
                return []
            return [self.element('p', text=value)]
        else:
            value = entity.printable_value(attr_name)
            if not value:
                return []
            return list(etree.fromstring(u"<root>{0}</root>".format(value)))
