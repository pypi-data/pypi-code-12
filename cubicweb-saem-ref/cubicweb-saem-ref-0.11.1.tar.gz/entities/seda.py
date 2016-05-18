#  coding: utf-8
# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""cubicweb-saem-ref entity's classes and adapters for SEDA classes"""

from lxml import etree

from cubicweb.uilib import cut
from cubicweb.entities import AnyEntity
from cubicweb.predicates import is_instance, is_in_state

from cubes.compound.entities import IClonableAdapter
from cubes.oaipmh.entities import OAISetSpec

from cubes.saem_ref import cwuri_url
from cubes.saem_ref.entities import AbstractXmlAdapter, oai

_ = unicode


class SEDAComponentIClonableAdapter(IClonableAdapter):
    """Cloning adapter for SEDA components."""
    rtype = 'seda_clone_of'
    skiprtypes = ()


class SEDAProfileIClonableAdapter(IClonableAdapter):
    """Cloning adapter for SEDA profiles."""
    __select__ = IClonableAdapter.__select__ & is_in_state('published')
    rtype = 'seda_replace'
    skiprtypes = ()


class SEDAProfile(AnyEntity):
    __regid__ = 'SEDAProfile'

    @property
    def archives(self):
        return self.reverse_seda_parent

    def dc_title(self):
        return self.title or self.ark

    def __getstate__(self):
        # Exclude ark from copy to have so that it can be generated for the clone
        odict = self.__dict__.copy()
        odict['cw_attr_cache'].pop('ark', None)
        return odict

    @property
    def predecessor(self):
        """The predecessor of the current profile, that is the one that has been replaced by it"""
        predecessors = self.seda_replace
        if predecessors:
            return predecessors[0]
        return None

    @property
    def successor(self):
        """The successor of the current profile, that is the one that has replaced it"""
        successors = self.reverse_seda_replace
        if successors:
            return successors[0]
        return None


class TransferringAgentOAISetSpec(OAISetSpec):
    """OAI-PMH set specifier to match SEDAProfile related to a transferring
    agent.
    """

    def setspecs(self, cnx):
        rset = cnx.execute(
            'Any A WHERE X archival_role R, R name "deposit", X ark A')
        desc = 'SEDAProfile with transferring agent identified by {0}'
        for value, in rset.rows:
            yield value, desc.format(value)

    def setspec_restrictions(self, value):
        qs = ('X seda_transferring_agent A, A archival_role R'
              ', R name "deposit", A ark %(value)s'
              ', X in_state ST, NOT ST name "draft"')
        return qs, {'value': value}


class SEDAProfileOAIPMHRecordAdapter(oai.OAIPMHActiveRecordAdapter):
    """OAI-PMH adapter for SEDAProfile entity type."""
    __select__ = oai.OAIPMHActiveRecordAdapter.__select__ & is_instance('SEDAProfile')
    metadata_view = 'saem_ref.seda02'

    @classmethod
    def set_definition(cls):
        specifier = oai.PublicETypeOAISetSpec(
            'SEDAProfile', cls.identifier_attribute, 'profile')
        specifier['transferring_agent'] = TransferringAgentOAISetSpec()
        return specifier


class ProfileArchiveObject(AnyEntity):
    __regid__ = 'ProfileArchiveObject'

    def dc_title(self):
        """Return the dc_title for an entity supporting seda_name relation."""
        if self.name.value:
            arch_title = u'({0})'.format(self.name.value)
        else:
            arch_title = u'#{0}'.format(self.eid)
        return u'{0} {1}'.format(self.dc_type(), arch_title)

    @property
    def name(self):
        return self.seda_name[0]

    @property
    def content_description(self):
        if self.seda_content_description:
            return self.seda_content_description[0]
        return None

    @property
    def access_restriction_code(self):
        if self.seda_access_restriction_code:
            return self.seda_access_restriction_code[0]
        return None

    @property
    def appraisal_rule(self):
        if self.seda_appraisal_rule:
            return self.seda_appraisal_rule[0]
        return None

    @property
    def first_level(self):
        """True if this document unit's parent is a profile"""
        return bool(self.seda_parent) and self.seda_parent[0].cw_etype == 'SEDAProfile'


class ProfileDocument(AnyEntity):
    __regid__ = 'ProfileDocument'

    @property
    def description(self):
        if self.seda_description:
            return self.seda_description[0]
        return None

    @property
    def character_set_code(self):
        if self.seda_character_set_code:
            return self.seda_character_set_code[0]
        return None

    @property
    def file_type_code(self):
        if self.seda_file_type_code:
            return self.seda_file_type_code[0]
        return None

    @property
    def document_type_code(self):
        return self.seda_document_type_code[0]

    def dc_title(self):
        dtype = self.document_type_code.seda_document_type_code_value[0].dc_title()
        if self.user_annotation:
            title = u'%s (%s)' % (cut(self.user_annotation, 100), dtype)
        else:
            title = u'%s #%s' % (dtype, self.eid)
        return title


def _seda_profile_element_dc_title(entity):
    """Return a dc_title for an "SEDA profile element"-like entity."""
    return u'{0} #{1}'.format(entity.dc_type(), entity.eid)


class SEDAContentDescription(AnyEntity):
    __regid__ = 'SEDAContentDescription'

    @property
    def description(self):
        if self.seda_description:
            return self.seda_description[0]
        return None

    @property
    def description_level(self):
        return self.seda_description_level[0]

    @property
    def keywords(self):
        return self.reverse_seda_keyword_of

    def dc_title(self):
        return _seda_profile_element_dc_title(self)


class SEDADescriptionLevel(AnyEntity):
    __regid__ = 'SEDADescriptionLevel'

    def dc_title(self):
        return _seda_profile_element_dc_title(self)


class SEDAAppraisalRule(AnyEntity):
    __regid__ = 'SEDAAppraisalRule'

    def dc_title(self):
        return _seda_profile_element_dc_title(self)

    @property
    def appraisal_rule_code(self):
        return self.seda_appraisal_rule_code[0]

    @property
    def appraisal_rule_duration(self):
        return self.seda_appraisal_rule_duration[0]


class SEDAAccessRestrictionCode(AnyEntity):
    __regid__ = 'SEDAAccessRestrictionCode'

    def dc_title(self):
        return _seda_profile_element_dc_title(self)


class SEDAName(AnyEntity):
    __regid__ = 'SEDAName'

    def dc_title(self):
        return self.printable_value('value') or self._cw._('<no value>')


class SEDADescription(AnyEntity):
    __regid__ = 'SEDADescription'

    def dc_title(self):
        return self.printable_value('value') or self._cw._('<no value>')


class SEDADate(AnyEntity):
    __regid__ = 'SEDADate'

    def dc_title(self):
        return self.printable_value('value') or self._cw._('<no value>')


class SEDAKeyword(AnyEntity):
    __regid__ = 'SEDAKeyword'

    @property
    def scheme(self):
        return self.seda_keyword_scheme[0]

    @property
    def concept(self):
        if self.seda_keyword_value:
            return self.seda_keyword_value[0]
        return None

    def dc_title(self):
        if self.concept:
            return self.concept.label()
        if self.scheme:
            return self._cw._('value from scheme "%s"') % self.scheme.dc_title()
        return self._cw._('<no value>')


# XSD transformation ###############################################################################

class XSDAttr(dict):
    """Simple object to define an xsd:attribute element.

    Params:

    * `name`, value for the 'name' attribute of the xsd:attribute

    * `type`, value for the 'type' attribute of the xsd:attribute

    * `cardinality`, optional cardinality that will be used to compute
      the 'use' attribute of the xsd:attribute (default to 'prohibited')

    * `value`, optional value for the 'fixed' attribute of the xsd:attribute
    """
    def __init__(self, name, xs_type, cardinality=None, value=None):
        assert cardinality in (None, '1', '0..1'), cardinality
        if cardinality is None:
            use = 'prohibited'
        elif cardinality == '1':
            use = 'required'
        else:
            use = 'optional'
        super(XSDAttr, self).__init__(name=name, type=xs_type, use=use)
        if value is not None:
            self['fixed'] = unicode(value)


LIST_VERSION_ID_2009 = XSDAttr('listVersionID', 'xsd:token', '1', 'edition 2009')
LIST_VERSION_ID_2011 = XSDAttr('listVersionID', 'xsd:token', '1', 'edition 2011')


class SEDA1XSDExport(AbstractXmlAdapter):
    """Adapter to build an XSD representation of a SEDA profile, using SEDA 1.0 specification"""
    __regid__ = 'SEDA-1.0.xsd'
    __select__ = is_instance('SEDAProfile')

    namespaces = {
        None: 'fr:gouv:culture:archivesdefrance:seda:v1.0',
        'xsd': 'http://www.w3.org/2001/XMLSchema',
        'qdt': 'fr:gouv:culture:archivesdefrance:seda:v1.0:QualifiedDataType:1',
        'udt': 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:10',
        'clmDAFFileTypeCode': 'urn:un:unece:uncefact:codelist:draft:DAF:fileTypeCode:2009-08-18',
        'clmIANACharacterSetCode':
        'urn:un:unece:uncefact:codelist:standard:IANA:CharacterSetCode:2007-05-14',
        'clmIANAMIMEMediaType':
        'urn:un:unece:uncefact:codelist:standard:IANA:MIMEMediaType:2008-11-12',
        'clm60133': 'urn:un:unece:uncefact:codelist:standard:6:0133:40106',
    }
    root_attributes = {
        'attributeFormDefault': 'unqualified',
        'elementFormDefault': 'qualified',
        'targetNamespace': 'fr:gouv:culture:archivesdefrance:seda:v1.0',
        'version': '1.0',
    }

    @property
    def file_name(self):
        """Return a file name for the dump"""
        return '%s.xsd' % self.entity.dc_title()

    def dump(self):
        """Return an XSD string for the adapted SEDA profile."""
        root = self.element('xsd:schema', attributes=self.root_attributes)
        self.xsd_transfer(root, self.entity)
        return etree.tostring(root, encoding=self.encoding, pretty_print=True, standalone=False)

    # business visit methods #######################################################################

    def xsd_transfer(self, parent, profile):
        """Append XSD elements for the profile to the given parent node."""
        transfer_node = self.xsd_element(parent, 'ArchiveTransfer',
                                         annotation=profile.title,
                                         xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        if profile.description:
            self.xsd_element(transfer_node, 'Comment', 'udt:TextType',
                             value=profile.printable_value('description', format='text/plain'),
                             xsd_attributes=[XSDAttr('languageID', 'xsd:language')])
        self.xsd_element(transfer_node, 'Date', 'udt:DateTimeType')
        self.xsd_element(transfer_node, 'TransferIdentifier', 'qdt:ArchivesIDType',
                         xsd_attributes=self.xsd_attributes_scheme())
        for archive in profile.archives:
            self.xsd_archive(transfer_node, archive)

    def xsd_agent(self, parent, agent, role, agent_type='OrganizationType', name_model='Name'):
        """Append XSD elements for the transferring/archival agency to the given parent node."""
        agent_node = self.xsd_element(parent, role, agent_type)
        self.xsd_element(agent_node, 'Identification', 'qdt:ArchivesIDType',
                         value=agent.ark,
                         xsd_attributes=self.xsd_attributes_scheme())
        self.xsd_element(agent_node, name_model, 'udt:TextType', agent.name,
                         xsd_attributes=[XSDAttr('languageID', 'xsd:language')])
        return agent_node

    def xsd_archive(self, parent, archive):
        """Append XSD elements for an archive to the given parent node."""
        archive_node = self.xsd_element(parent, 'Archive', 'ArchiveType',
                                        cardinality=archive.user_cardinality,
                                        annotation=archive.user_annotation,
                                        xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        # hard-coded description's language
        self.xsd_element(archive_node, 'DescriptionLanguage', 'qdt:CodeLanguageType',
                         value='fra',
                         xsd_attributes=[LIST_VERSION_ID_2011])
        self.xsd_element(archive_node, 'Name', 'udt:TextType',
                         value=archive.name.value,
                         annotation=archive.name.user_annotation,
                         xsd_attributes=[XSDAttr('languageID', 'xsd:language')])
        if archive.appraisal_rule:
            self.xsd_appraisal_rule(archive_node, archive.appraisal_rule)
        self.xsd_access_restriction(archive_node, archive.access_restriction_code)
        self.xsd_content_description(archive_node, archive.content_description)
        self.xsd_children(archive_node, archive)

    archive_object_tag_name = 'ArchiveObject'

    def xsd_archive_object(self, parent, archive_object):
        """Append XSD elements for the archive object to the given parent node."""
        ao_node = self.xsd_element(parent, self.archive_object_tag_name, 'ArchiveObjectType',
                                   cardinality=archive_object.user_cardinality,
                                   annotation=archive_object.user_annotation,
                                   xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        self.xsd_element(ao_node, 'Name', 'udt:TextType',
                         value=archive_object.name.value,
                         annotation=archive_object.name.user_annotation,
                         xsd_attributes=[XSDAttr('languageID', 'xsd:language')])
        if archive_object.appraisal_rule:
            self.xsd_appraisal_rule(ao_node, archive_object.appraisal_rule)
        if archive_object.access_restriction_code:
            self.xsd_access_restriction(ao_node, archive_object.access_restriction_code)
        if archive_object.content_description:
            self.xsd_content_description(ao_node, archive_object.content_description)
        self.xsd_children(ao_node, archive_object)
        return ao_node

    def xsd_document(self, parent, document):
        """Append XSD elements for the document to the given parent node."""
        document_node = self.xsd_element(parent, 'Document', 'DocumentType',
                                         cardinality=document.user_cardinality,
                                         annotation=document.user_annotation,
                                         xsd_attributes=[XSDAttr('Id', 'xsd:ID')])

        def safe_cardinality(entity):
            return getattr(entity, 'user_cardinality', None)

        def safe_concept_value(entity, rtype):
            return _concept_value(entity, rtype) if entity is not None else None

        self.xsd_element(document_node, 'Attachment', 'qdt:ArchivesBinaryObjectType',
                         xsd_attributes=[
                             XSDAttr('format', 'clmDAFFileTypeCode:FileTypeCodeType',
                                     cardinality=safe_cardinality(document.file_type_code),
                                     value=safe_concept_value(document.file_type_code,
                                                              'seda_file_type_code_value')),
                             XSDAttr('characterSetCode',
                                     'clmIANACharacterSetCode:CharacterSetCodeContentType',
                                     cardinality=safe_cardinality(document.character_set_code),
                                     value=safe_concept_value(document.character_set_code,
                                                              'seda_character_set_code_value')),
                             # hard-coded attributes
                             XSDAttr('mimeCode', 'clmIANAMIMEMediaType:MIMEMediaTypeContentType'),
                             XSDAttr('encodingCode',
                                     'clm60133:CharacterSetEncodingCodeContentType'),
                             XSDAttr('uri', 'xsd:anyURI'),
                             XSDAttr('filename', 'xsd:string'),
                         ])
        self.xsd_element(document_node, 'Type', 'qdt:CodeDocumentType',
                         value=_concept_value(document.document_type_code,
                                              'seda_document_type_code_value'),
                         xsd_attributes=[LIST_VERSION_ID_2009])
        if document.description:
            self.xsd_description(document_node, document.description)

    def xsd_appraisal_rule(self, parent, appraisal_rule):
        ar_node = self.xsd_element(parent, 'Appraisal', 'AppraisalRuleType',
                                   cardinality=appraisal_rule.user_cardinality,
                                   annotation=appraisal_rule.user_annotation,
                                   xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        ar_code = appraisal_rule.appraisal_rule_code
        ar_code_value = _concept_value(ar_code, 'seda_appraisal_rule_code_value')
        self.xsd_element(ar_node, 'Code', 'qdt:CodeAppraisalType',
                         value=ar_code_value,
                         annotation=ar_code.user_annotation,
                         xsd_attributes=[LIST_VERSION_ID_2009])
        ar_duration = appraisal_rule.seda_appraisal_rule_duration[0]
        ar_duration_value = _concept_value(ar_duration, 'seda_appraisal_rule_duration_value')
        self.xsd_element(ar_node, 'Duration', 'qdt:ArchivesDurationType',
                         value=ar_duration_value,
                         annotation=ar_duration.user_annotation)
        # hard-coded start date
        self.xsd_element(ar_node, 'StartDate', 'udt:DateType')

    access_restriction_tag_name = 'AccessRestrictionRule'

    def xsd_access_restriction(self, parent, access_restriction):
        """Append XSD elements for an access restriction to the given parent node."""
        ar_node = self.xsd_element(parent, self.access_restriction_tag_name,
                                   'AccessRestrictionRulesType',
                                   cardinality=access_restriction.user_cardinality,
                                   annotation=access_restriction.user_annotation,
                                   xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        ar_code = _concept_value(access_restriction, 'seda_access_restriction_code_value')
        self.xsd_element(ar_node, 'Code', 'qdt:CodeAccessRestrictionType',
                         value=ar_code,
                         xsd_attributes=[LIST_VERSION_ID_2009])
        # hard-coded start date
        self.xsd_element(ar_node, 'StartDate', 'udt:DateType')

    def xsd_content_description(self, parent, content_description):
        """Append XSD elements for a description content to the given parent node"""
        cd_node = self.xsd_element(parent, 'ContentDescription', 'ContentDescriptionType',
                                   cardinality=content_description.user_cardinality,
                                   annotation=content_description.user_annotation,
                                   xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        self.xsd_description_level(cd_node, content_description.description_level)
        for dt in ('oldest', 'latest'):
            date_entities = getattr(content_description, 'seda_%s_date' % dt)
            if date_entities:
                date_entity = date_entities[0]
                self.xsd_element(cd_node, '%sDate' % dt.capitalize(), 'udt:DateType',
                                 # default python formating '%Y-%m-%d' is fine
                                 value=date_entity.value,
                                 cardinality=date_entity.user_cardinality,
                                 annotation=date_entity.user_annotation)
        if content_description.description:
            self.xsd_description(cd_node, content_description.description)
        for keyword in content_description.keywords:
            self.xsd_keyword(cd_node, keyword)

    def xsd_description_level(self, parent, description_level):
        """Append XSD elements for a description level to the given parent node"""
        level = _concept_value(description_level, 'seda_description_level_value')
        self.xsd_element(parent, 'DescriptionLevel', 'qdt:CodeDescriptionLevelType',
                         annotation=description_level.user_annotation,
                         value=level,
                         xsd_attributes=[LIST_VERSION_ID_2009])

    def xsd_description(self, parent, description):
        """Append XSD elements for a description to the given parent node"""
        self.xsd_element(parent, 'Description', 'udt:TextType',
                         cardinality=description.user_cardinality,
                         annotation=description.user_annotation,
                         value=description.value,
                         xsd_attributes=[XSDAttr('languageID', 'xsd:language')])

    # extracted from xsd_keyword to allow parametrization for SEDA 1.0 vs 0.2 generation
    kw_tag_name = 'Keyword'
    kw_content_tag_type = 'qdt:KeywordContentType'
    kw_content_tag_attributes = [XSDAttr('role', 'xsd:token'),
                                 XSDAttr('languageID', 'xsd:language')]

    def xsd_keyword(self, parent, keyword):
        """Append XSD elements for a keyword to the given parent node"""
        kw_node = self.xsd_element(parent, self.kw_tag_name, 'KeywordType',
                                   cardinality=keyword.user_cardinality,
                                   annotation=keyword.user_annotation,
                                   xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        if keyword.concept:
            url = cwuri_url(keyword.concept)
            content = keyword.concept.label()
        else:
            url = content = None
        self.xsd_element(kw_node, 'KeywordContent', self.kw_content_tag_type,
                         value=content,
                         xsd_attributes=self.kw_content_tag_attributes)
        self.xsd_element(kw_node, 'KeywordReference', 'qdt:ArchivesIDType',
                         value=url,
                         xsd_attributes=self.xsd_attributes_scheme(keyword.scheme))

    @staticmethod
    def xsd_attributes_scheme(scheme=None):
        """Return a list of :class:`XSDAttr` for a scheme definition, with some proper values
        specified if a scheme is given.
        """
        attributes = [
            XSDAttr('schemeID', 'xsd:token'),
            XSDAttr('schemeName', 'xsd:string'),
            XSDAttr('schemeAgencyName', 'xsd:string'),
            XSDAttr('schemeVersionID', 'xsd:token'),
            XSDAttr('schemeDataURI', 'xsd:anyURI'),
            XSDAttr('schemeURI', 'xsd:anyURI'),
        ]
        if scheme is not None:
            # schemeURI
            attributes[-1]['fixed'] = cwuri_url(scheme)
            attributes[-1]['use'] = 'required'
            # schemeID
            attributes[0]['fixed'] = scheme.ark
            attributes[0]['use'] = 'required'
            # schemeName
            if scheme.title:
                attributes[1]['fixed'] = scheme.title
                attributes[1]['use'] = 'required'
        return attributes

    # generic methods ##############################################################################

    def xsd_children(self, parent, entity):
        """Iter on archive/archive object (unité documentaire) children, which may be either
        archive objects or documents, and append XSD elements for them to the given parent node.
        """
        for archive_object_or_document in entity.reverse_seda_parent:
            if archive_object_or_document.cw_etype == 'ProfileDocument':
                self.xsd_document(parent, archive_object_or_document)
            else:
                assert archive_object_or_document.cw_etype == 'ProfileArchiveObject'
                self.xsd_archive_object(parent, archive_object_or_document)

    def xsd_element(self, parent, name, xs_type=None, value=None, cardinality='1', annotation=None,
                    xsd_attributes=()):
        """Generic function to build a XSD element tag.

        Params:

        * `parent`, the parent etree node

        * `name`, value for the 'name' attribute of the xsd:element

        * `xs_type`, optional value for the 'type' attribute of the xsd:element

        * `value`, optional value for the 'fixed' attribute of the xsd:element

        * `cardinality`, optional string for the 'minOccurs' and/or 'maxOccurs' attributes of the
          xsd:element - may be one of '1', '0..1', '1..n', '0..n'

        * `annotation`, optional comment to add as annotation node for explanation of the element

        * `xsd_attributes`, list of :class:`XSDAttr` defining xsd:attributes children of the
          xsd:element
        """
        assert name, 'cannot build a XSD element tag with an empty name %r' % name
        attributes = {'name': name}
        if xs_type is not None:
            attributes['type'] = xs_type
        if value is not None:
            attributes['fixed'] = unicode(value)
        assert cardinality in ('0..1', '0..n', '1', '1..n')
        if cardinality != '1':
            if cardinality[0] == '0':
                attributes['minOccurs'] = '0'
            if cardinality[-1] == 'n':
                attributes['maxOccurs'] = 'unbounded'
        element = self.element('xsd:element', parent, attributes)
        if annotation:
            annotation_node = self.element('xsd:annotation', element)
            self.element('xsd:documentation', annotation_node).text = annotation
        ct = self.element('xsd:complexType', element)
        seq = self.element('xsd:sequence', ct)
        for xsd_attr in xsd_attributes:
            self.element('xsd:attribute', ct, xsd_attr)
        return seq

    # compatibility testing ########################################################################

    def blockers(self):
        """Yield messages describing a problem that prevents the given profile to be exported."""
        profile = self.entity
        if not profile.archives:
            yield (profile.eid, _('the profile should have at least a document unit'))
        else:
            for archive in profile.archives:
                if archive.user_cardinality in ('0..1', '0..n'):
                    yield (archive.eid, _('0..1 and 0..n cardinalities are forbidden on '
                                          'first-level document unit'))
                if not archive.content_description:
                    yield (archive.eid,
                           _('first level document unit must have a content description defined'))
                elif archive.content_description.user_cardinality == '0..1':
                    yield (archive.eid, _('0..1 cardinality is not allowed on content '
                                          'description of a first-level document unit'))
                if not archive.access_restriction_code:
                    yield (archive.eid, _('first level document unit must have an access '
                                          'restriction defined'))
                elif archive.access_restriction_code.user_cardinality == '0..1':
                    yield (archive.eid, _('0..1 cardinality is not allowed on access '
                                          'restriction of a first-level document unit'))

    def is_compatible(self):
        """Return True if the adapted entity may be exported in the format handled by this adapter.
        """
        try:
            next(self.blockers())
            return False
        except StopIteration:
            return True


def _concept_value(entity, relation_name):
    """Return the value of the concept linked to the entity through the given relation or None
    """
    rset = entity.related(relation_name)
    if rset:
        return rset.one().label()
    return None


class SEDA02XSDExport(SEDA1XSDExport):
    """Adapter to build an XSD representation of a SEDA profile, using SEDA 0.2 specification"""
    __regid__ = 'SEDA-0.2.xsd'

    namespaces = SEDA1XSDExport.namespaces.copy()
    namespaces[None] = 'fr:gouv:ae:archive:draft:standard_echange_v0.2'
    namespaces['qdt'] = 'fr:gouv:ae:archive:draft:standard_echange_v0.2:QualifiedDataType:1'
    namespaces['udt'] = 'urn:un:unece:uncefact:data:standard:UnqualifiedDataType:6'

    root_attributes = SEDA1XSDExport.root_attributes.copy()
    root_attributes['targetNamespace'] = 'fr:gouv:ae:archive:draft:standard_echange_v0.2'
    root_attributes['version'] = '1.1'

    def xsd_archive(self, parent, archive):
        """Append XSD elements for an archive to the given parent node."""
        archive_node = self.xsd_element(parent, 'Contains', 'ArchiveType',
                                        cardinality=archive.user_cardinality,
                                        annotation=archive.user_annotation,
                                        xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        # hard-coded description's language
        self.xsd_element(archive_node, 'DescriptionLanguage', 'qdt:CodeLanguageType',
                         value='fr',
                         xsd_attributes=[LIST_VERSION_ID_2009])
        self.xsd_element(archive_node, 'Name', 'udt:TextType',
                         value=archive.seda_name[0].value,
                         annotation=archive.seda_name[0].user_annotation,
                         xsd_attributes=[XSDAttr('languageID', 'xsd:language')])
        # in SEDA 0.2, description level is on the archive element, not on its content description
        content_description = archive.content_description
        self.xsd_description_level(archive_node, content_description.description_level)
        if archive.appraisal_rule:
            self.xsd_appraisal_rule(archive_node, archive.appraisal_rule)
        # in SEDA 0.2, access restriction is not mandatory, though it is in our model
        self.xsd_access_restriction(archive_node, archive.access_restriction_code)
        self.xsd_content_description(archive_node, content_description)
        self.xsd_children(archive_node, archive)

    def xsd_content_description(self, parent, content_description):
        """Append XSD elements for a description content to the given parent node"""
        cd_node = self.xsd_element(parent, 'ContentDescription', 'ContentDescriptionType',
                                   cardinality=content_description.user_cardinality,
                                   annotation=content_description.user_annotation,
                                   xsd_attributes=[XSDAttr('Id', 'xsd:ID')])
        for dt in ('oldest', 'latest'):
            date_entities = getattr(content_description, 'seda_%s_date' % dt)
            if date_entities:
                date_entity = date_entities[0]
                self.xsd_element(cd_node, '%sDate' % dt.capitalize(), 'udt:DateType',
                                 # default python formating '%Y-%m-%d' is fine
                                 value=date_entity.value,
                                 cardinality=date_entity.user_cardinality,
                                 annotation=date_entity.user_annotation)
        if content_description.description:
            self.xsd_description(cd_node, content_description.description)
        # in SEDA 0.2, content description has a description language as well
        self.xsd_element(cd_node, 'DescriptionLanguage', 'qdt:CodeLanguageType',
                         value='fr',
                         xsd_attributes=[LIST_VERSION_ID_2009])
        for keyword in content_description.keywords:
            self.xsd_keyword(cd_node, keyword)
        # in SEDA 0.2, there may be some access restriction on the content description but it's on
        # the archive in our model

    def xsd_archive_object(self, parent, archive_object):
        """Append XSD elements for the archive object to the given parent node."""
        ao_node = super(SEDA02XSDExport, self).xsd_archive_object(parent, archive_object)
        # in SEDA 0.2, description level is on the archive object element, not on its content
        # description
        if archive_object.content_description:
            content_description = archive_object.content_description
            self.xsd_description_level(ao_node, content_description.description_level)
        else:
            self.xsd_element(ao_node, 'DescriptionLevel', 'qdt:CodeDescriptionLevelType',
                             xsd_attributes=[LIST_VERSION_ID_2009])

    # in SEDA 0.2, ArchiveObject tag name is 'Contains' (as for Archive)
    archive_object_tag_name = 'Contains'
    # in SEDA 0.2, AccessRestrictionRule tag name is 'AccessRestriction'
    access_restriction_tag_name = 'AccessRestriction'
    # in SEDA 0.2, keyword tag name is 'ContentDescriptive', not 'Keyword' and keyword content type
    # is TextType and there is no 'role' attribute
    kw_tag_name = 'ContentDescriptive'
    kw_content_tag_type = 'udt:TextType'
    kw_content_tag_attributes = [XSDAttr('languageID', 'xsd:language')]
