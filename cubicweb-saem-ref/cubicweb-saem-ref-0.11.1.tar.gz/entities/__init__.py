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
"""cubicweb-saem-ref entity's classes"""

from lxml import etree

from logilab.common.decorators import monkeypatch

from cubicweb.view import Adapter, EntityAdapter
from cubicweb.predicates import match_kwargs, relation_possible, is_instance
from cubicweb.entities import AnyEntity, fetch_config, authobjs


class ARKGeneratorMixIn(object):
    """Entity adapter for ARK unique identifier generation"""
    __abstract__ = True
    __regid__ = 'IARKGenerator'
    __select__ = match_kwargs('naa_what')

    def generate_ark(self):
        """Return a new ARK identifier as unicode"""
        return u'{0}/{1}'.format(self.cw_extra_kwargs['naa_what'], self.assign_name())

    def assign_name(self):
        """Assign and return a new name part of the ARK identifier"""
        raise NotImplementedError()


class ARKExtIdentifierGenerator(ARKGeneratorMixIn, Adapter):
    """Simple adapter for allocation of ark to object which are not (yet) entities."""

    def assign_name(self):
        """Return a new unique identifier as unicode"""
        dbh = self._cw.repo.system_source.dbhelper
        for sql in dbh.sqls_increment_sequence('ext_ark_count'):
            cu = self._cw.system_sql(sql)
        count = cu.fetchone()[0]
        return u'ext-{0:09d}'.format(count)


class ARKCWIdentifierGenerator(ARKGeneratorMixIn, Adapter):
    """saem_ref.IARKGenerator entity adapter generating ARK like identifier during non-production
    phase.
    """
    __select__ = ARKGeneratorMixIn.__select__ & match_kwargs('eid', 'etype')

    def assign_name(self):
        eid = self.cw_extra_kwargs['eid']
        etype = self.cw_extra_kwargs['etype']
        prefix = {
            "Agent": u"a",
            "SEDAProfile": u"p",
            "Concept": u"c",
            "ConceptScheme": u"v",
        }.get(etype, u"")
        return u'{0}{1:09d}'.format(prefix, eid)


class ArkNAALocator(EntityAdapter):
    """Adapter responsible to retrieve the proper ARK Name Assigning Authority depending on the
    entity type
    """
    __abstract__ = True
    __regid__ = 'IArkNAALocator'

    def naa_what(self):
        """Return the ARK NameAssigningAuthority entity or None if not specified"""
        raise NotImplementedError()


class DirectArkNAALocator(ArkNAALocator):
    """Return NAA specified through the ark_naa relation"""
    __select__ = relation_possible('ark_naa')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'ark_naa' in getattr(self.entity, 'cw_edited', {}):
            return self._cw.entity_from_eid(self.entity.cw_edited['ark_naa']).what
        elif self.entity.ark_naa:
            return self.entity.ark_naa[0].what
        return None


class AgentArkNAALocator(ArkNAALocator):
    """Return NAA specified through the authority to which the agent belong"""
    __select__ = is_instance('Agent')

    def naa_what(self):
        # entity is usually not yet created, since ark has to be generated before entity creation
        if 'authority' in getattr(self.entity, 'cw_edited', {}):
            authority = self._cw.entity_from_eid(self.entity.cw_edited['authority'])
            if authority.ark_naa:
                return authority.ark_naa[0].what
        elif self.entity.authority and self.authority[0].ark_naa:
            return self.authority[0].ark_naa[0].what
        return None


class ConceptArkNAALocator(ArkNAALocator):
    """Return NAA for Concept, usually specified through a record in transaction data"""
    __select__ = is_instance('Concept')

    def naa_what(self):
        if 'concept_scheme' in self._cw.transaction_data:
            scheme = self._cw.entity_from_eid(self._cw.transaction_data['concept_scheme'])
            return scheme.cw_adapt_to(self.__regid__).naa_what()
        elif self.entity.in_scheme:  # entity may not yet be related to its scheme
            return self.entity.in_scheme[0].cw_adapt_to(self.__regid__).naa_what()
        return None


class ExternalUri(AnyEntity):
    __regid__ = 'ExternalUri'
    fetch_attrs, cw_fetch_order = fetch_config(('uri',))


@monkeypatch(authobjs.CWUser, methodname='naa')
@property
def naa(self):
    if self.authority and self.authority[0].ark_naa:
        return self.authority[0].ark_naa[0]
    return None


def substitute_xml_prefix(prefix_name, namespaces):
    """Given an XML prefixed name in the form `'ns:name'`, return the string `'{<ns_uri>}name'`
    where `<ns_uri>` is the URI for the namespace prefix found in `namespaces`.

    This new string is then suitable to build an LXML etree.Element object.

    Example::

        >>> substitude_xml_prefix('xlink:href', {'xlink': 'http://wwww.w3.org/1999/xlink'})
        '{http://www.w3.org/1999/xlink}href'

    """
    try:
        prefix, name = prefix_name.split(':', 1)
    except ValueError:
        return prefix_name
    assert prefix in namespaces, 'Unknown namespace prefix: {0}'.format(prefix)
    return '{{{0}}}'.format(namespaces[prefix]) + name


class AbstractXmlAdapter(EntityAdapter):
    """Abstract adapter to produce XML documents."""

    content_type = 'text/xml'
    encoding = 'utf-8'
    namespaces = {}

    @property
    def file_name(self):
        """Return a file name for the dump."""
        raise NotImplementedError

    def dump(self):
        """Return an XML string for the adapted entity."""
        raise NotImplementedError

    def element(self, tag, parent=None, attributes=None, text=None):
        """Generic function to build a XSD element tag.

        Params:

        * `name`, value for the 'name' attribute of the xsd:element

        * `parent`, the parent etree node

        * `attributes`, dictionary of attributes
        """
        attributes = attributes or {}
        tag = substitute_xml_prefix(tag, self.namespaces)
        for attr, value in attributes.items():
            newattr = substitute_xml_prefix(attr, self.namespaces)
            attributes[newattr] = value
            if newattr != attr:
                attributes.pop(attr)
        if parent is None:
            elt = etree.Element(tag, attributes, nsmap=self.namespaces)
        else:
            elt = etree.SubElement(parent, tag, attributes)
        if text is not None:
            elt.text = text
        return elt
