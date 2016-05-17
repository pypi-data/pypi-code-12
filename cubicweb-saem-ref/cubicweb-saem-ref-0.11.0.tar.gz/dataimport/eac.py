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
"""cubicweb-saem-ref dataimport utilities for EAC-CPF (Encoded Archival
Context -- Corporate Bodies, Persons, and Families).
"""

from collections import deque
import datetime
from functools import wraps
import inspect
import logging
from uuid import uuid4

from dateutil.parser import parse as parse_date
from lxml import etree

from cubicweb import Binary
from cubicweb.dataimport.importer import ExtEntity
from cubes.skos import to_unicode
from cubes.saem_ref import eactype_mapping, eacaddress_mapping, eacmaintenancetype_mapping

TYPE_MAPPING = eactype_mapping.copy()
TYPE_MAPPING['human'] = u'person'

ETYPES_ORDER_HINT = ('AgentKind', 'PhoneNumber', 'PostalAddress', 'Agent',
                     'AgentPlace', 'Mandate', 'LegalStatus', 'History',
                     'Structure', 'AgentFunction', 'Occupation', 'GeneralContext',
                     'AssociationRelation', 'ChronologicalRelation', 'HierarchicalRelation',
                     'EACResourceRelation', 'ExternalUri', 'EACSource',
                     'Activity')


class InvalidEAC(RuntimeError):
    """EAC input is malformed."""


class InvalidXML(RuntimeError):
    """EAC input has an invalid XML format"""


class MissingTag(RuntimeError):
    """Mandatory tag is missing in EAC input"""

    def __init__(self, tag, tag_parent=None):
        super(MissingTag, self).__init__()
        self.tag = tag
        self.tag_parent = tag_parent


def external_uri(uri):
    values = [unicode(uri)]
    return ExtEntity('ExternalUri', uri, {'uri': set(values), 'cwuri': set(values)})


def filter_none(func):
    """Filter None value from a generator function."""
    def wrapped(*args, **kwargs):
        for x in func(*args, **kwargs):
            if x is not None:
                yield x
    return wraps(func)(wrapped)


def filter_empty(func):
    """Filter out empty ExtEntity (i.e. with empty ``values`` attribute)."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        for extentity in func(self, *args, **kwargs):
            if extentity.values:
                yield extentity
    return wrapper


def elem_maybe_none(func):
    """Method decorator for external entity builder function handling the case
    of `elem` being None.
    """
    if inspect.isgeneratorfunction(func):
        def wrapped(self, elem, *args, **kwargs):
            if elem is None:
                return
            for extentity in func(self, elem, *args, **kwargs):
                yield extentity
    else:
        def wrapped(self, elem, *args, **kwargs):
            if elem is None:
                return None
            else:
                return func(self, elem, *args, **kwargs)
    return wraps(func)(wrapped)


def add_xml_wrap_for(*etypes):
    """Add an `xml_wrap` attribute in ExtEntity's values dictionnary."""
    def decorator(func):
        def wrapped(self, elem):
            objectXMLWrap = self._elem_find(elem, 'eac:objectXMLWrap')
            xmlwrap = None
            if objectXMLWrap is not None:
                nchildren = len(objectXMLWrap)
                if nchildren >= 1:
                    xmlwrap = objectXMLWrap[0]
                if nchildren > 1:
                    msg = self._('multiple children elements found in {0}').format(
                        objectXMLWrap)
                    self.import_log.record_warning(msg, line=objectXMLWrap.line)
            attribute_added = False
            for extentity in func(self, elem):
                if xmlwrap is not None and extentity.etype in etypes:
                    # prevent association of xmlwrap to several extentities.
                    assert not attribute_added, 'xml_wrap attribute already added'
                    extentity.values.setdefault('xml_wrap', set([])).add(
                        Binary(etree.tostring(xmlwrap, encoding='utf-8'))
                    )
                    attribute_added = True
                yield extentity
        return wraps(func)(wrapped)
    return decorator


def relate_to_agent_through(etype, rtype):
    """Add an ``rtype`` relationship from ``etype`` to the imported agent."""
    def decorator(func):
        if inspect.isgeneratorfunction(func):
            def wrapper(self, *args, **kwargs):
                for extentity in func(self, *args, **kwargs):
                    if extentity.etype == etype:
                        extentity.values.setdefault(rtype, set()).add(self.agent.extid)
                    yield extentity
        else:
            def wrapper(self, *args, **kwargs):
                extentity = func(self, *args, **kwargs)
                if extentity and extentity.etype == etype:
                    extentity.values.setdefault(rtype, set()).add(self.agent.extid)
                return extentity
        return wraps(func)(wrapper)
    return decorator


def add_citations_for(etype):
    """Handle import of citation tag for `etype` ExtEntity that is yielded by
    decorated method.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, elem):
            for extentity in func(self, elem):
                if extentity.etype == etype:
                    for citation in self.build_citation(elem):
                        extentity.values.setdefault(
                            'has_citation', set()).add(citation.extid)
                        yield citation
                yield extentity
        return wrapper
    return decorator


def require_tag(tagname):
    """Method decorator handling a mandatory tag within a XML element."""
    def warn(self, elem):
        self.import_log.record_warning(
            self._('expecting a %s tag in element %s, found none') %
            (tagname, elem.tag), line=elem.sourceline)

    def decorator(func):
        # pylint: disable=protected-access
        if inspect.isgeneratorfunction(func):
            def wrapped(self, elem, *args, **kwargs):
                if self._elem_find(elem, tagname) is None:
                    warn(self, elem)
                    return
                for extentity in func(self, elem, *args, **kwargs):
                    yield extentity
        else:
            def wrapped(self, elem, *args, **kwargs):
                if self._elem_find(elem, tagname) is None:
                    warn(self, elem)
                    return None
                return func(self, elem, *args, **kwargs)
        return wraps(func)(wrapped)

    return decorator


def trace_extentity(instance):
    """Decorator for `build_` methods tracing ExtEntities built from a given
    XML element.
    """
    def decorator(func):
        if inspect.isgeneratorfunction(func):
            def wrapper(elem, *args, **kwargs):
                for extentity in func(elem, *args, **kwargs):
                    instance.record_visited(elem, extentity)
                    yield extentity
        else:
            def wrapper(elem, *args, **kwargs):
                extentity = func(elem, *args, **kwargs)
                if extentity is not None:
                    instance.record_visited(elem, extentity)
                return extentity
        return wraps(func)(wrapper)
    return decorator


def equivalent_concept(tagname, etype):
    """Method decorator indicating that a sub-tag may have a vocabularySource attribute indicating
    that a relation to some ExternalUri object should be drown from any entity of type `etype` built
    by decorated method.
    """
    def decorator(func):
        @wraps(func)
        def wrapped(self, elem, *args, **kwargs):
            subelem = self._elem_find(elem, tagname)
            if subelem is not None:
                extid = subelem.attrib.get('vocabularySource')
                if extid is not None:
                    yield external_uri(extid)
            else:
                extid = None

            def update_extentity(extentity):
                if extid is not None and extentity.etype == etype:
                    extentity.values['equivalent_concept'] = set([extid])

            if inspect.isgeneratorfunction(func):
                for extentity in func(self, elem, *args, **kwargs):
                    update_extentity(extentity)
                    yield extentity
            else:
                extentity = func(self, elem, *args, **kwargs)
                update_extentity(extentity)
                yield extentity
        return wrapped
    return decorator


class EACCPFImporter(object):
    """Importer for EAC-CPF data.

    The importer will generate `extid`s using the `extid_generator` function
    if specified or use `uuid.uuid4` to generate unique `extid`s.

    During import the `agent` attribute is set to the external entity of the
    imported Agent.

    Ref: http://eac.staatsbibliothek-berlin.de/fileadmin/user_upload/schema/cpfTagLibrary.html
    """
    def __init__(self, fpath, import_log, _, extid_generator=None):
        try:
            tree = etree.parse(fpath)
        except etree.XMLSyntaxError as exc:
            raise InvalidXML(str(exc))
        self._ = _
        self._root = tree.getroot()
        self.namespaces = self._root.nsmap.copy()
        self.namespaces['eac'] = self.namespaces.pop(None)
        self.import_log = import_log
        if extid_generator is None:
            def extid_generator():
                return str(uuid4())
        self._gen_extid = extid_generator
        self.agent = ExtEntity('Agent', None, {})
        # Store a mapping of XML elements to produced ExtEntities
        self._visited = {}

    def __getattribute__(self, name):
        attr = super(EACCPFImporter, self).__getattribute__(name)
        if name.startswith('build_'):
            return trace_extentity(self)(attr)
        return attr

    def record_visited(self, elem, extentity):
        assert extentity.extid, extentity
        self._visited.setdefault(elem, set([])).add(extentity.extid)

    def not_visited(self):
        """Yield (tagname, sourceline) items corresponding to XML elements not
        used to build any ExtEntity.
        """
        visited = self._visited
        ns = self.namespaces['eac']
        queue = deque(self._root)
        # These elements contain other ones which are known to be handled.
        container_tags = ['control', 'cpfDescription', 'identity',
                          'maintenanceHistory', 'sources', 'description',
                          'mandates', 'places', 'occupations', 'relations']
        containers = ['{{{0}}}{1}'.format(ns, tag) for tag in container_tags]
        while queue:
            elem = queue.popleft()
            if (not isinstance(elem, etree._Element) or
                    isinstance(elem, etree._Comment)):
                continue
            if elem in visited:
                continue
            if elem.tag not in containers:
                yield elem.tag.replace('{' + ns + '}', ''), elem.sourceline
            else:
                queue.extend(elem)

    def _elem_find(self, elem, path, method='find'):
        """Wrapper around lxml.etree.Element find* methods to support
        namespaces also for old lxml versions.
        """
        finder = getattr(elem, method)
        try:
            return finder(path, self.namespaces)
        except TypeError:
            # In old lxml, find() does not accept namespaces argument.
            path = path.split(':', 1)
            try:
                ns, path = path
            except ValueError:
                # path has no namespace
                pass
            else:
                path = '{' + self.namespaces[ns] + '}' + path
            return finder(path)

    def _elem_findall(self, *args):
        return self._elem_find(*args, method='findall')

    @filter_empty
    def external_entities(self):
        """Parse a EAC XML file to and yield external entities."""
        # control element.
        control = self._elem_find(self._root, 'eac:control')
        for extentity in self.parse_control(control):
            yield extentity
        # Agents (identity tags) are within cpfDescription tag.
        cpf_desc = self._elem_find(self._root, 'eac:cpfDescription')
        if cpf_desc is None:
            raise MissingTag('cpfDescription')
        # identity element.
        identity = self._elem_find(cpf_desc, 'eac:identity')
        if identity is None:
            raise MissingTag('identity', 'cpfDescription')
        for extentity in self.parse_identity(identity):
            yield extentity
        # description element.
        description = self._elem_find(cpf_desc, 'eac:description')
        if description is not None:
            for extentity in self.parse_description(description):
                yield extentity
        # relations element.
        for extentity in self.parse_relations(cpf_desc):
            yield extentity
        # Agent is complete.
        self.record_visited(self._root, self.agent)
        yield self.agent

    def parse_identity(self, identity):
        """Parse the `identity` tag and yield external entities, possibly
        updating agent's `values` dict.
        """
        # entityId
        isni = self._elem_find(identity, 'eac:entityId')
        if isni is not None and isni.text:
            self.record_visited(isni, self.agent)
            self.agent.values['isni'] = set([unicode(isni.text)])
        # entityType
        akind = self._elem_find(identity, 'eac:entityType')
        if akind is None:
            raise MissingTag('entityType', 'identity')
        agent_kind = self.build_agent_kind(akind)
        yield agent_kind
        self.agent.values['agent_kind'] = set([agent_kind.extid])
        for name_entry in self._elem_findall(identity, 'eac:nameEntry'):
            self.record_visited(name_entry, self.agent)
            if self._elem_find(name_entry, 'eac:authorizedForm') is not None:
                break
        else:
            msg = self._('found no nameEntry tag within an authorizedForm '
                         'element, using %s instead') % name_entry
            self.import_log.record_info(msg, line=name_entry.sourceline)
        part = self._elem_find(name_entry, 'eac:part')
        self.agent.values['name'] = set([unicode(part.text)])

    @filter_none
    def parse_description(self, description):
        """Parse the `description` tag and yield external entities, possibly
        updating agent's `values` dict.
        """
        # dates.
        daterange = description.xpath('eac:existDates/eac:dateRange',
                                      namespaces=self.namespaces)
        if daterange:
            elem = daterange[0]
            self.record_visited(elem, self.agent)
            self.record_visited(elem.getparent(), self.agent)
            dates = self.parse_daterange(elem)
            if dates:
                self.agent.values.update(dates)
        # address.
        for place in self.find_nested(description, 'eac:place', 'eac:places'):
            for extentity in self.build_place(place):
                yield extentity
        # additional EAC-CPF information.
        for legal_status in self._elem_findall(description, 'eac:legalStatus'):
            for extentity in self.build_legal_status(legal_status):
                yield extentity
        # mandate
        for mandate in self.find_nested(description, 'eac:mandate', 'eac:mandates'):
            for extentity in self.build_mandate(mandate):
                yield extentity
        # history
        for history in self._elem_findall(description, 'eac:biogHist'):
            for extentity in self.build_history(history):
                yield extentity
        # structure
        for structure in self._elem_findall(description, 'eac:structureOrGenealogy'):
            yield self.build_structure(structure)
        # function
        for function in self.find_nested(description, 'eac:function', 'eac:functions'):
            for extentity in self.build_function(function):
                yield extentity
        # occupation
        for occupation in self.find_nested(description, 'eac:occupation',
                                           'eac:occupations'):
            for extentity in self.build_occupation(occupation):
                yield extentity
        # general context
        for context in self._elem_findall(description, 'eac:generalContext'):
            for extentity in self.build_generalcontext(context):
                yield extentity

    def find_nested(self, elem, tagname, innertag):
        """Return a list of element with `tagname` within `element` possibly
        nested within `innertag`.
        """
        all_elems = self._elem_findall(elem, tagname)
        wrapper = self._elem_find(elem, innertag)
        if wrapper is not None:
            all_elems.extend(self._elem_findall(wrapper, tagname))
        return all_elems

    def parse_tag_description(self, elem, tagname='eac:descriptiveNote',
                              attrname='description'):
        """Return a dict with `attrname` and `attrname`_format retrieved from
        a description-like tag.
        """
        elems = self._elem_findall(elem, tagname)
        if len(elems) > 1:
            self.import_log.record_warning(self._(
                'found multiple %s tag within %s element, only one will be '
                'used.') % (tagname, elem.tag), line=elem.sourceline)
        elem = elems[0] if elems else None
        values = {}
        if elem is not None:
            parsed = self.parse_tag_content(elem)
            values.update(zip((attrname, attrname + '_format'),
                              (set([p]) for p in parsed)))
        return values

    def parse_tag_content(self, elem):
        """Parse the content of an element be it text of HTML and return the
        content along with MIME type.
        """
        assert elem is not None, 'unexpected empty element'
        text = elem.text.strip() if elem.text else None
        if text:
            desc, desc_format = unicode(text), u'text/plain'
        else:
            ptag = '{%(eac)s}p' % self.namespaces
            desc = '\n'.join(etree.tostring(child, encoding=unicode,
                                            method='html').strip()
                             for child in elem.iterchildren(ptag)
                             if len(child) != 0 or child.text)
            if desc:
                desc_format = u'text/html'
            else:
                self.import_log.record_warning(self._(
                    'element %s has no text nor children, no content '
                    'extracted') % elem.tag, line=elem.sourceline)
                desc, desc_format = None, None
        return desc, desc_format

    @elem_maybe_none
    def build_agent_kind(self, elem):
        """Build a AgentKind external entity"""
        # Map EAC entity types to our terminolgy.
        kind = TYPE_MAPPING.get(elem.text, elem.text)
        agentkind_id = 'agentkind/' + kind
        return ExtEntity('AgentKind', agentkind_id, {'name': set([unicode(kind)])})

    @elem_maybe_none
    @relate_to_agent_through('LegalStatus', 'legal_status_agent')
    @filter_empty
    @add_citations_for('LegalStatus')
    @equivalent_concept('eac:term', 'LegalStatus')
    def build_legal_status(self, elem, **kwargs):
        """Build a `LegalStatus` external entity.

        Extra `kwargs` are passed to `parse_tag_description`.
        """
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None and term.text:
            values['term'] = set([unicode(term.text)])
        values.update(**self.parse_tag_description(elem, **kwargs))
        dateelem = self._elem_find(elem, 'eac:dateRange')
        dates = self.parse_daterange(dateelem)
        if dates:
            values.update(dates)
        legalstatus = ExtEntity('LegalStatus', self._gen_extid(), values)
        if dateelem is not None:
            self.record_visited(dateelem, legalstatus)
        yield legalstatus

    @elem_maybe_none
    @relate_to_agent_through('Mandate', 'mandate_agent')
    @filter_empty
    @add_citations_for('Mandate')
    @equivalent_concept('eac:term', 'Mandate')
    def build_mandate(self, elem, **kwargs):
        """Build a `Mandate` external entity.

        Extra `kwargs` are passed to `parse_tag_description`.
        """
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None and term.text:
            values['term'] = set([unicode(term.text)])
        values.update(**self.parse_tag_description(elem, **kwargs))
        dateelem = self._elem_find(elem, 'eac:dateRange')
        dates = self.parse_daterange(dateelem)
        if dates:
            values.update(dates)
        yield ExtEntity('Mandate', self._gen_extid(), values)

    @elem_maybe_none
    def build_citation(self, elem):
        """Build a `Citation` external entity."""
        for citation_elem in self._elem_findall(elem, "eac:citation"):
            note = citation_elem.text.strip() if citation_elem.text else u''
            uri = citation_elem.attrib.get('{%(xlink)s}href' % self.namespaces)
            if not note and not uri:
                msg = self._('element {0} has no text nor (valid) link').format(
                    etree.tostring(citation_elem))
                self.import_log.record_warning(msg, line=citation_elem.sourceline)
                return
            values = {}
            if uri:
                values['uri'] = set([unicode(uri)])
            if note:
                values['note'] = set([unicode(note)])
                if u'<span>' in note:
                    values['note_format'] = set([u'text/html'])
            yield ExtEntity('Citation', self._gen_extid(), values)

    @relate_to_agent_through('History', 'history_agent')
    @filter_empty
    @add_citations_for('History')
    @elem_maybe_none
    def build_history(self, elem):
        """Build a `History` external entity."""
        desc, desc_format = self.parse_tag_content(elem)
        values = {}
        if desc:
            values.update(text=set([desc]), text_format=set([desc_format]))
        yield ExtEntity('History', self._gen_extid(), values)

    @elem_maybe_none
    @relate_to_agent_through('Structure', 'structure_agent')
    def build_structure(self, elem):
        """Build a `Structure` external entity."""
        desc, desc_format = self.parse_tag_content(elem)
        if desc:
            values = {'description': set([desc]),
                      'description_format': set([desc_format])}
            return ExtEntity('Structure', self._gen_extid(), values)

    @relate_to_agent_through('AgentPlace', 'place_agent')
    @filter_empty
    @add_citations_for('AgentPlace')
    @equivalent_concept('eac:placeEntry', 'AgentPlace')
    def build_place(self, elem):
        """Build a AgentPlace external entity"""
        values = {}
        role = self._elem_find(elem, 'eac:placeRole')
        if role is not None:
            values['role'] = set([unicode(role.text)])
        entry = self._elem_find(elem, 'eac:placeEntry')
        if entry is not None:
            values['name'] = set([unicode(entry.text)])
        for address in self._elem_findall(elem, 'eac:address'):
            for extentity in self.build_address(address):
                values['place_address'] = set([extentity.extid])
                yield extentity
        yield ExtEntity('AgentPlace', self._gen_extid(), values)

    def build_address(self, elem):
        """Build `PostalAddress`s external entity"""
        address_entity = {}
        for line in self._elem_findall(elem, 'eac:addressLine'):
            if 'localType' in line.attrib:
                attr = dict(eacaddress_mapping).get(line.attrib['localType'])
                if attr:
                    address_entity.setdefault(attr, set()).add(
                        unicode(line.text))
        yield ExtEntity('PostalAddress', self._gen_extid(), address_entity)

    @relate_to_agent_through('AgentFunction', 'function_agent')
    @filter_empty
    @add_citations_for('AgentFunction')
    @equivalent_concept('eac:term', 'AgentFunction')
    def build_function(self, elem):
        """Build a `AgentFunction`s external entities"""
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None:
            values['name'] = set([unicode(term.text)])
        values.update(self.parse_tag_description(elem))
        yield ExtEntity('AgentFunction', self._gen_extid(), values)

    @relate_to_agent_through('Occupation', 'occupation_agent')
    @filter_empty
    @add_citations_for('Occupation')
    @equivalent_concept('eac:term', 'Occupation')
    def build_occupation(self, elem):
        """Build a `Occupation`s external entities"""
        values = {}
        term = self._elem_find(elem, 'eac:term')
        if term is not None:
            values['term'] = set([unicode(term.text)])
        values.update(self.parse_tag_description(elem))
        dateelem = self._elem_find(elem, 'eac:dateRange')
        dates = self.parse_daterange(dateelem)
        if dates:
            values.update(dates)
        yield ExtEntity('Occupation', self._gen_extid(), values)

    @relate_to_agent_through('GeneralContext', 'general_context_of')
    @filter_empty
    @add_citations_for('GeneralContext')
    def build_generalcontext(self, elem):
        """Build a `GeneralContext` external entity"""
        values = {}
        content, content_format = self.parse_tag_content(elem)
        if content:
            values.update({
                'content': set([content]),
                'content_format': set([content_format]),
            })
        yield ExtEntity('GeneralContext', self._gen_extid(), values)

    @elem_maybe_none
    def parse_daterange(self, elem):
        """Parse a `dateRange` tag and return a dict mapping `start_date` and
        `end_date` to parsed date range.
        """
        values = {}
        for eactag, attrname in zip(('eac:fromDate', 'eac:toDate'),
                                    ('start_date', 'end_date')):
            date = self.parse_date(self._elem_find(elem, eactag))
            if date:
                values[attrname] = set([date])
        return values

    @elem_maybe_none
    def parse_date(self, elem):
        """Parse a date-like element"""
        def record_warning(msg):
            self.import_log.record_warning(msg % {'e': etree.tostring(elem)},
                                           line=elem.sourceline)
        standard_date = elem.attrib.get('standardDate')
        if standard_date:
            date = standard_date
        else:
            for attr in ('notBefore', 'notAfter'):
                if elem.attrib.get(attr):
                    record_warning(self._('found an unsupported %s attribute in date '
                                          'element %%(e)s') % attr)
            # Using element's text.
            date = elem.text
        # Set a default value for month and day; the year should always be
        # given.
        default = datetime.datetime(9999, 1, 1)
        try:
            pdate = parse_date(date, default=default)
        except ValueError as exc:
            record_warning(self._('could not parse date %(e)s'))
            return None
        except Exception as exc:  # pylint: disable=broad-except
            # Usually a bug in dateutil.parser.
            record_warning(self._(
                'unexpected error during parsing of date %%(e)s: %s') %
                to_unicode(exc))
            logger = logging.getLogger('cubicweb.saem_ref')
            logger.exception(self._('unhandled exception while parsing date %r'), date)
            return None
        else:
            if pdate.year == default.year:
                record_warning(self._('could not parse a year from date element %(e)s'))
                return None
            return pdate.date()

    def parse_relations(self, cpf_description):
        """Parse the `relations` tag and yield external entities, possibly
        updating agent's `values` dict.
        """
        relations = self._elem_find(cpf_description, 'eac:relations')
        if relations is None:
            return
        # cpfRelation.
        for cpfrel in self._elem_findall(relations, 'eac:cpfRelation'):
            for extentity in self.build_relation(cpfrel):
                yield extentity
        # resourceRelation.
        for rrel in self._elem_findall(relations, 'eac:resourceRelation'):
            for extentity in self.build_resource_relation(rrel):
                yield extentity

    @add_xml_wrap_for('AssociationRelation', 'ChronologicalRelation',
                      'HierarchicalRelation')
    def build_relation(self, elem):
        """Build a relation between agents external entity (with proper type)."""
        relationship = elem.attrib.get('cpfRelationType')
        if relationship is None:
            self.import_log.record_warning(self._(
                'found no cpfRelationType attribute in element %s, defaulting '
                'to associative') % etree.tostring(elem),
                line=elem.sourceline)
            relationship = 'associative'
        try:
            # "other_role" (resp. "agent_role") role designates the object of the relation (resp.
            # the agent described in the EAC-CPF instance).
            # See: http://eac.staatsbibliothek-berlin.de/fileadmin/user_upload/schema/cpfTagLibrary.html#cpfRelationType # noqa pylint: disable=line-too-long
            # In case the EAC relation is not qualified, we assume the object is the "parent" (or
            # oldest) in the relation.
            etype, other_role, agent_role = {
                'hierarchical': ('HierarchicalRelation',
                                 'hierarchical_parent', 'hierarchical_child'),
                'hierarchical-parent': ('HierarchicalRelation',
                                        'hierarchical_parent', 'hierarchical_child'),
                'hierarchical-child': ('HierarchicalRelation',
                                       'hierarchical_child', 'hierarchical_parent'),
                'temporal': ('ChronologicalRelation',
                             'chronological_predecessor', 'chronological_successor'),
                'temporal-earlier': ('ChronologicalRelation',
                                     'chronological_predecessor', 'chronological_successor'),
                'temporal-later': ('ChronologicalRelation',
                                   'chronological_successor', 'chronological_predecessor'),
                'associative': ('AssociationRelation',
                                'association_to', 'association_from'),
            }[relationship]
        except KeyError:
            self.import_log.record_warning(self._(
                'unsupported cpfRelationType %s in element %s, skipping')
                % (relationship, etree.tostring(elem)),
                line=elem.sourceline)
            return
        obj_uri = elem.attrib.get('{%(xlink)s}href' % self.namespaces)
        if obj_uri is None:
            self.import_log.record_warning(self._('found a cpfRelation without any object (no '
                                                  'xlink attribute), skipping'),
                                           line=elem.sourceline)
            return
        rentry = self._elem_find(elem, 'eac:relationEntry')
        if rentry is not None and rentry.text.strip():
            yield ExtEntity('Agent', obj_uri, {'name': set([unicode(rentry.text)]),
                                               'agent_kind': set(['agentkind/unknown-agent-kind'])})
        else:
            yield external_uri(obj_uri)
        values = {agent_role: set([self.agent.extid]), other_role: set([obj_uri])}
        dates = self.parse_daterange(
            self._elem_find(elem, 'eac:dateRange'))
        if dates:
            if etype == 'ChronologicalRelation':
                self.import_log.record_warning(
                    self._('ignoring dates on %s since chronological relation '
                           'does not support dates') % etree.tostring(elem)
                )
            else:
                values.update(dates)
        values.update(self.parse_tag_description(elem))
        yield ExtEntity(etype, self._gen_extid(), values)

    @add_xml_wrap_for('EACResourceRelation')
    def build_resource_relation(self, elem):
        """Build a `EACResourceRelation` external entity (along with
        ExternalUri entities).
        """
        obj_uri = elem.attrib.get('{%(xlink)s}href' % self.namespaces)
        if obj_uri is None:
            self.import_log.record_warning(self._(
                'found a resourceRelation without any object (no xlink '
                'attribute), skipping'), line=elem.sourceline)
            return
        yield external_uri(obj_uri)
        values = {
            'resource_relation_resource': set([obj_uri]),
            'resource_relation_agent': set([self.agent.extid]),
        }
        resource_role = elem.attrib.get('{%(xlink)s}role' % self.namespaces)
        if resource_role:
            values['resource_role'] = set([unicode(resource_role)])
        agent_role = elem.attrib.get('resourceRelationType')
        if agent_role:
            values['agent_role'] = set([unicode(agent_role)])
        dates = self.parse_daterange(self._elem_find(elem, 'eac:dateRange'))
        if dates:
            values.update(dates)
        values.update(self.parse_tag_description(elem))
        yield ExtEntity('EACResourceRelation', self._gen_extid(), values)

    @filter_none
    def parse_control(self, control):
        """Parse the `control` tag."""
        record_id = self._elem_find(control, 'eac:recordId')
        if record_id is not None and record_id.text and record_id.text.strip():
            self.agent.extid = record_id.text.strip()
            self.record_visited(record_id, self.agent)
        else:
            self.agent.extid = self._gen_extid()
            self.import_log.record_warning(self._(
                'found no recordId element in control tag, using %s as cwuri') %
                self.agent.extid)
        for elem in control.xpath('eac:sources/eac:source',
                                  namespaces=self.namespaces):
            for extentity in self.build_source(elem):
                yield extentity
        for elem in control.xpath('eac:maintenanceHistory/eac:maintenanceEvent',
                                  namespaces=self.namespaces):
            for extentity in self.build_maintenance_event(elem):
                yield extentity

    def build_maintenance_event(self, elem):
        """Parse a `maintenanceEvent` tag, yielding a prov:Activity external
        entity along with necessary Agents.
        """
        values = {'generated': set([self.agent.extid])}
        event_type = self.parse_event_type(self._elem_find(elem, 'eac:eventType'))
        if event_type is not None:
            values['type'] = set([event_type])
        date = self._elem_find(elem, 'eac:eventDateTime')
        if date is not None:
            dtattr = date.attrib.get('standardDateTime')
            if dtattr:
                try:
                    event_date = parse_date(dtattr)
                except ValueError:
                    self.import_log.record_warning(
                        self._('could not parse date from %s') % etree.tostring(date),
                        line=date.sourceline)
                else:
                    values['start'] = set([event_date])
                    values['end'] = set([event_date])
        values.update(self.parse_tag_description(elem, 'eac:eventDescription'))
        agent = self._elem_find(elem, 'eac:agent')
        if agent is not None and agent.text:
            agent_type = self._elem_find(elem, 'eac:agentType')
            agent_kind = self.build_agent_kind(agent_type)
            if agent_kind is not None:
                yield agent_kind
                agent_kind_extid = agent_kind.extid
            else:
                agent_kind_extid = 'agentkind/unknown-agent-kind'
            agent_id = self._gen_extid()
            yield ExtEntity('Agent', agent_id,
                            {'name': set([unicode(agent.text)]),
                             'agent_kind': set([agent_kind_extid])})
            values['associated_with'] = set([agent_id])
        yield ExtEntity('Activity', self._gen_extid(), values)

    @elem_maybe_none
    def parse_event_type(self, elem):
        """Parse an `eventType` element and try to match a prov:type to build a
        prov:Activity.
        """
        event_type = elem.text.strip() if elem.text else None
        if event_type:
            type_mapping = eacmaintenancetype_mapping.copy()
            type_mapping['derived'] = u'create'
            type_mapping['updated'] = u'modify'
            try:
                event_type = type_mapping[event_type.lower()]
            except KeyError:
                self.import_log.record_warning(self._(
                    'eventType %s does not match the PROV-O vocabulary, respective Activity will '
                    'not have a `type` attribute set.') % event_type, line=elem.sourceline)
                return None
            return event_type

    @relate_to_agent_through('EACSource', 'source_agent')
    @filter_empty
    @add_xml_wrap_for('EACSource')
    def build_source(self, elem):
        """Parse a `source` tag, yielding EACSource external entities.
        """
        values = {}
        url = elem.attrib.get('{%(xlink)s}href' % self.namespaces)
        if url is not None:
            values['url'] = set([unicode(url)])
        entry = self._elem_find(elem, 'eac:sourceEntry')
        if entry is not None and entry.text:
            values['title'] = set([unicode(entry.text)])
        values.update(self.parse_tag_description(elem))
        yield ExtEntity('EACSource', self._gen_extid(), values)
