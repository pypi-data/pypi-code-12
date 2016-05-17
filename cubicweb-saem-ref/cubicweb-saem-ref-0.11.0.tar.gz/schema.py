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
"""cubicweb-saem-ref schema"""

from yams.buildobjs import (EntityType, RelationDefinition, String, Date, Bytes, Int,
                            RichString, ComputedRelation, DEFAULT_RELPERMS)
from yams.constraints import UniqueConstraint, BoundaryConstraint, Attribute

from cubicweb.schema import (RO_ATTR_PERMS, ERQLExpression, RRQLExpression,
                             RQLConstraint, RQLVocabularyConstraint, WorkflowableEntityType,
                             make_workflowable)
from cubicweb.schemas.base import ExternalUri

from cubes.skos.schema import ConceptScheme
from cubes.prov.schema import Agent

from cubes.saem_ref import (PERMISSIONS_GRAPHS, OUTER_RELATIVE_PERM_RELATIONS,
                            optional_relations, mandatory_rdefs)

_ = unicode


def dated_entity_type(cls):
    """Class decorator adding `start_date` and `end_date` attribute to an
    EntityType.
    """
    cls.add_relation(Date(constraints=[BoundaryConstraint(
        '<=', Attribute('end_date'), msg=_('start date must be less than end date'))]),
        name='start_date')
    cls.add_relation(Date(), name='end_date')
    return cls


def xml_wrap(cls):
    """Class decorator adding an `xml_wrap` attribute to an EntityType."""
    desc = _('XML elements not contained in EAC-CPF namespace')
    cls.add_relation(Bytes(description=desc), name='xml_wrap')
    return cls


def seda_profile_element(cardinalities=None, default_cardinality=None):
    """Class decorator adding attributes to configure a SEDA field.
    """
    def decorator(cls):
        if cardinalities:
            cls.add_relation(String(required=True, vocabulary=cardinalities,
                                    default=default_cardinality,
                                    internationalizable=True),
                             name='user_cardinality')
        cls.add_relation(String(fulltextindexed=True),
                         name='user_annotation')
        return cls
    return decorator


def publication_permissions(cls):
    """Set __permissions__ of `cls` entity type class preventing modification
    when not in state "draft".
    """
    cls.__permissions__ = cls.__permissions__.copy()
    cls.__permissions__['update'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users"), '
                       'X in_state ST, ST name "draft"'),
    )
    cls.__permissions__['delete'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users"), '
                       'X in_state ST, ST name "draft"'),
    )
    return cls


def groups_permissions(cls):
    """Set __permissions__ of `cls` entity type class preventing modification
    when user is not in managers or users group.
    """
    cls.__permissions__ = cls.__permissions__.copy()
    cls.__permissions__['update'] = (
        ERQLExpression('U in_group G, G name IN ("managers", "users")', 'U'),
    )
    return cls


def _rel_expr(rtype, role):
    return {'subject': 'X {rtype} A',
            'object': 'A {rtype} X'}[role].format(rtype=rtype)


def relative_update_permissions_through(*relations, **options):
    """Class decorator setting 'update' permission on entity type class relative to
    `(rtype, role)` relations.

    This is for use on entities whose parent is reachable through non mandatory relations, others
    should be handled by :func:`graph_set_etypes_update_permissions`.
    """
    handle_not_exists = options.pop('may_not_exists', True)
    assert not options, 'unknown options: %s' % options

    def set_perms(cls):
        cls.__permissions__ = cls.__permissions__.copy()
        exprs = []
        for rtype, role in relations:
            relexpr = _rel_expr(rtype, role)
            if handle_not_exists:
                exprs.append('NOT EXISTS({relexpr}), U in_group G, '
                             'G name IN ("managers", "users")'.format(relexpr=relexpr))
            exprs.append('{relexpr}, U has_update_permission A'.format(relexpr=relexpr))
        for action in ('update', 'delete'):
            cls.__permissions__[action] = tuple(ERQLExpression(e) for e in exprs)
        return cls
    return set_perms


def graph_set_etypes_update_permissions(schema, graph, etype):
    """Add `action` permissions for all entity types in the composite `graph`
    with root `etype`. Respective permissions that are inserted on each
    entity type are relative to the "parent" in the relation from this
    entity type walking up to the graph root.

    So for instance, calling `set_etype_permissions('R', 'update')`
    on a schema where `A related_to B` and `R root_of B` one will get:

    * "U has_update_permission R, R root_of X" for `B` entity type and,
    * "U has_update_permission P, X related_to P" for `A` entity type.

    If an entity type in the graph is reachable through multiple relations, a
    permission for each of this relation will be inserted so that if any of
    these match, the permission check will succeed.
    """
    structure = graph.parent_structure(etype)
    optionals = optional_relations(schema, structure)
    for child, relations in structure.iteritems():
        skiprels = optionals.get(child, set())
        exprs = []
        for rtype, role in relations:
            if (rtype, role) in skiprels:
                continue
            relexpr = _rel_expr(rtype, role)
            exprs.append('{relexpr}, U has_update_permission A'.format(relexpr=relexpr))
        if exprs:
            for action in ('update', 'delete'):
                schema[child].set_action_permissions(action,
                                                     tuple(ERQLExpression(e) for e in exprs))


_RELATIVE_PERM_RELATIONS_CONSISTENCY_CHECK = set()


def relative_write_permissions_of(role):
    """Relation definition class decorator setting permissions for 'add' and 'delete' actions
    related to `role` target.

    Important notes:

    - this is for use with non mandatory relations or relation to some entity which doesn't belong
      to the compound graph, others should be handled by :func:`graph_set_write_rdefs_permissions`,

    - the decorated relation definition must be added to `cubicweb.server.ON_COMMIT_ADD_RELATIONS`.
    """
    def set_perms(cls):
        _RELATIVE_PERM_RELATIONS_CONSISTENCY_CHECK.add(getattr(cls, 'name', cls.__name__))
        if not cls.__permissions__:
            cls.__permissions__ = DEFAULT_RELPERMS
        cls.__permissions__ = cls.__permissions__.copy()
        var = {'object': 'O', 'subject': 'S'}[role]
        expr = 'U has_update_permission {0}'.format(var)
        for action in ('add', 'delete'):
            cls.__permissions__[action] = (RRQLExpression(expr),)
        return cls
    return set_perms


def graph_set_write_rdefs_permissions(schema, graph, etype):
    """Set 'add' and 'delete' permissions for all mandatory relation definitions in the composite
    `graph` with root `etype`.

    Respective permissions that are inserted on each relation definition are relative to the
    "parent" in the relation from this entity type walking up to the graph root.

    Relations which are not mandatory or which are not part of the graph structure should be handled
    manually.
    """
    structure = graph.parent_structure(etype)
    for rdef, parent_role in mandatory_rdefs(schema, structure):
        var = {'object': 'O', 'subject': 'S'}[parent_role]
        expr = 'U has_update_permission {0}'.format(var)
        for action in ('add', 'delete'):
            rdef.set_action_permissions(action, (RRQLExpression(expr), ))


# Disable "update" for ExternalUri as these should only come from imported data
# and are meant to only be created or deleted.
ExternalUri.__permissions__ = ExternalUri.__permissions__.copy()
ExternalUri.__permissions__['update'] = ()


# Customization of Agent entity type.
make_workflowable(Agent)
groups_permissions(Agent)
Agent.add_relation(String(required=True, fulltextindexed=True), name='name')
Agent.add_relation(String(unique=True,
                          description=_('International Standard Name Identifier')),
                   name='isni')
dated_entity_type(Agent)


# Customization of skos schema.
make_workflowable(ConceptScheme)
publication_permissions(ConceptScheme)


class Authority(EntityType):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    name = String(required=True, fulltextindexed=True, unique=True)


class user_authority(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': (),
    }
    name = 'authority'
    subject = 'CWUser'
    object = 'Authority'
    cardinality = '?*'
    inlined = True


class agent_authority(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', RRQLExpression('U authority O'),),
        'delete': (),
    }
    name = 'authority'
    subject = 'Agent'
    object = 'Authority'
    cardinality = '1*'
    composite = 'object'
    inlined = True


class agent_user(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers',),
        'delete': ('managers',),
    }
    subject = 'Agent'
    object = 'CWUser'
    cardinality = '??'
    inlined = True
    description = _('the application user related to this agent')
    constraints = [
        RQLConstraint('S agent_kind K, K name "person"'),
        RQLConstraint('NOT EXISTS(O authority A) '
                      'OR EXISTS(O authority B, S authority B)'),
    ]


class contact_point(RelationDefinition):
    subject = 'Agent'
    object = 'Agent'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('O agent_kind K, K name "person"'),
        RQLConstraint('S authority A, O authority A'),
        RQLVocabularyConstraint('O in_state ST, ST name "published"'),
    ]
    description = _('set an agent of kind "person" as the contact point of an '
                    'agent of kind "authority"')


class archival_agent(RelationDefinition):
    subject = 'Agent'
    object = 'Agent'
    cardinality = '?*'
    description = _('the archival agent responsible for dealing with the agent '
                    'documents')
    constraints = [RQLConstraint('O archival_role AR, AR name "archival"'),
                   RQLConstraint('S authority A, O authority A'),
                   RQLVocabularyConstraint('O in_state ST, ST name "published"')]


class ArchivalRole(EntityType):
    """An archival role determines the kind of action (e.g. deposit or control)
    an agent may perform on an archive entity.
    """
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': ('managers', ),
        'delete': ('managers', ),
    }
    name = String(required=True, unique=True, internationalizable=True)


class archival_role(RelationDefinition):
    subject = 'Agent'
    object = 'ArchivalRole'
    cardinality = '**'
    description = _('the agent archival role (producer, control, etc.)')


# EAC-CPF model elements for Agent #############################################

class AgentFunction(EntityType):
    """The function of an Agent"""
    name = String(fulltextindexed=True, internationalizable=True)
    description = RichString(fulltextindexed=True)
    __unique_together__ = [('name', 'function_agent')]


class function_agent(RelationDefinition):
    subject = 'AgentFunction'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True


class phone_number(RelationDefinition):
    subject = 'Agent'
    object = 'PhoneNumber'
    cardinality = '*1'
    composite = 'subject'
    fulltext_container = 'subject'


class AgentPlace(EntityType):
    """Qualified relation between an Agent and a PostalAddress"""
    name = String(fulltextindexed=True,
                  description=_('encoded information about the address (e.g. '
                                '"Paris, France")'))
    role = String(description=_('contextual role the address has in relation '
                                'with the agent (e.g. "home")'),
                  internationalizable=True)
    __unique_together__ = [('role', 'place_agent', 'place_address')]


class place_address(RelationDefinition):
    subject = 'AgentPlace'
    object = 'PostalAddress'
    cardinality = '?1'
    inlined = True
    composite = 'subject'
    fulltext_container = 'subject'


class place_agent(RelationDefinition):
    subject = 'AgentPlace'
    object = 'Agent'
    cardinality = '1*'
    inlined = True
    composite = 'object'
    fulltext_container = 'object'


class postal_address(ComputedRelation):
    rule = 'P place_agent S, P place_address O'


class AgentKind(EntityType):
    """A kind of agent (e.g. "person", "authority" or "family")"""
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'update': (),
        'delete': (),
    }
    name = String(required=True, unique=True, internationalizable=True)


class agent_kind(RelationDefinition):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users'),
        'delete': (RRQLExpression('O name "unknown-agent-kind"'),),
    }
    subject = 'Agent'
    object = 'AgentKind'
    cardinality = '1*'
    inlined = True


class related_concept_scheme(RelationDefinition):
    subject = 'Agent'
    object = 'ConceptScheme'
    cardinality = '**'
    description = _('concept schemes used by the agent')


class _agent_relation(RelationDefinition):
    """Abstract relation between agents"""
    subject = None
    object = ('Agent', 'ExternalUri')
    cardinality = '1*'
    inlined = True


class GeneralContext(EntityType):
    """Information about the general social and cultural context of an agent"""
    content = RichString(fulltextindexed=True)


class general_context_of(RelationDefinition):
    subject = 'GeneralContext'
    object = 'Agent'
    cardinality = '1*'
    inlined = True
    composite = 'object'
    fulltext_container = 'object'


@xml_wrap
@dated_entity_type
class AssociationRelation(EntityType):
    """Association relation between agents"""
    description = RichString()


class association_from(_agent_relation):
    subject = 'AssociationRelation'


class association_to(_agent_relation):
    subject = 'AssociationRelation'


@xml_wrap
class ChronologicalRelation(EntityType):
    """Chronological relation between agents"""
    description = RichString()


class chronological_predecessor(_agent_relation):
    subject = 'ChronologicalRelation'


class chronological_successor(_agent_relation):
    subject = 'ChronologicalRelation'


@xml_wrap
@dated_entity_type
class HierarchicalRelation(EntityType):
    """Hierarchical relation between agents"""
    description = RichString()


class hierarchical_parent(_agent_relation):
    subject = 'HierarchicalRelation'


class hierarchical_child(_agent_relation):
    subject = 'HierarchicalRelation'


class generated(RelationDefinition):
    subject = 'Activity'
    object = ('Agent', 'Concept', 'ConceptScheme')


class used(RelationDefinition):
    subject = 'Activity'
    object = ('Agent', 'Concept', 'ConceptScheme')


@dated_entity_type
class Mandate(EntityType):
    """Reference text coming from an authority"""
    term = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)


@dated_entity_type
class LegalStatus(EntityType):
    """Information relative to the legal status of an authority"""
    term = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)


class History(EntityType):
    """Biographical or historical information"""
    text = RichString(fulltextindexed=True)


class Structure(EntityType):
    """Information about the structure of an authority"""
    description = RichString(fulltextindexed=True)


@dated_entity_type
class Occupation(EntityType):
    term = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)


class occupation_agent(RelationDefinition):
    subject = 'Occupation'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('occupation in which the person works or has worked')


class mandate_agent(RelationDefinition):
    subject = 'Mandate'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('mandate of an Agent')


class legal_status_agent(RelationDefinition):
    subject = 'LegalStatus'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('legal status of an Agent')


class structure_agent(RelationDefinition):
    subject = 'Structure'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('information about the structure of an Agent')


class history_agent(RelationDefinition):
    subject = 'History'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True
    description = _('information about the history of an Agent')


class Citation(EntityType):
    note = RichString()
    uri = String()


class has_citation(RelationDefinition):
    subject = ('GeneralContext', 'Mandate', 'Occupation', 'History',
               'AgentFunction', 'LegalStatus', 'AgentPlace')
    object = 'Citation'
    cardinality = '*?'
    composite = 'subject'
    description = _('reference to an external citation resource')


@xml_wrap
@dated_entity_type
class EACResourceRelation(EntityType):
    """Represent a relation between an Agent and a remote resource in the
    EAC-CPF model.
    """
    agent_role = String(description=_('type of relation the agent has to the resource'),
                        internationalizable=True)
    resource_role = String(description=_('type or nature of the remote resource'),
                           internationalizable=True)
    description = RichString(fulltextindexed=True)


class resource_relation_agent(RelationDefinition):
    subject = 'EACResourceRelation'
    object = 'Agent'
    cardinality = '1*'
    inlined = True
    composite = 'object'
    fulltext_container = 'object'


class resource_relation_resource(RelationDefinition):
    subject = 'EACResourceRelation'
    object = 'ExternalUri'
    cardinality = '1*'
    inlined = True


@xml_wrap
class EACSource(EntityType):
    """A source used to establish the description of an Agent"""
    title = String(fulltextindexed=True)
    url = String()
    description = RichString(fulltextindexed=True)


class source_agent(RelationDefinition):
    subject = 'EACSource'
    object = 'Agent'
    cardinality = '1*'
    composite = 'object'
    fulltext_container = 'object'
    inlined = True


class vocabulary_source(RelationDefinition):
    subject = ('Mandate', 'LegalStatus', 'AgentFunction', 'AgentPlace',
               'Occupation')
    object = 'ConceptScheme'
    cardinality = '?*'


class equivalent_concept(RelationDefinition):
    subject = ('Mandate', 'LegalStatus', 'AgentFunction', 'AgentPlace',
               'Occupation')
    object = ('ExternalUri', 'Concept')
    constraints = [RQLVocabularyConstraint('S vocabulary_source SC, O in_scheme SC')]
    cardinality = '?*'
    # relation with 'ExternalUri' as object can't be inlined because of a limitation of
    # data-import's (massive) store
    inlined = False


# ARK ##########################################################################

class ark(RelationDefinition):
    __permissions__ = RO_ATTR_PERMS
    subject = ('Agent', 'ConceptScheme', 'Concept', 'SEDAProfile')
    object = 'String'
    description = _('ARK Identifier - will be generated if not specified')
    constraints = [UniqueConstraint()]
    cardinality = '11'


class ArkNameAssigningAuthority(EntityType):
    """Name Assigning Authority (NAA) for ARK generation."""
    who = String(required=True, unique=True,
                 description=_('official organization name'))
    what = Int(required=True, unique=True,
               description=_('Name Assigning Authority Number (NAAN)'))


class _ark_naa(RelationDefinition):
    name = 'ark_naa'
    object = 'ArkNameAssigningAuthority'
    inlined = True


class authority_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', ),
        'delete': ('managers', ),
    }
    subject = 'Authority'
    cardinality = '?*'
    description = _("ARK identifier Name Assigning Authority (NAA) - "
                    "you'll need one to start creating objects")


class profile_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users',),
        'delete': (),
    }
    subject = 'SEDAProfile'
    cardinality = '1*'
    description = _("ARK identifier Name Assigning Authority (NAA) for this profile")


class other_ark_naa(_ark_naa):
    __permissions__ = {
        'read': ('managers', 'users', 'guests'),
        'add': ('managers', 'users',),
        'delete': (),
    }
    subject = ('ConceptScheme', 'SKOSSource')
    cardinality = '?*'
    description = _("ARK identifier Name Assigning Authority (NAA), "
                    "necessary to create ARK for concepts which don't have one yet.")


# SEDA #######################################################################

@publication_permissions
class SEDAProfile(WorkflowableEntityType):
    """a SEDA profile allows to restrict the `SEDA schema`_ by generating an XML schema (XSD) that
    may be transferred to SEDA compliant platforms (eg Alfresco and As@lae).

    .. _`SEDA schema`:http://www.archivesdefrance.culture.gouv.fr/seda/api/index.html
    """
    title = String(fulltextindexed=True)
    description = RichString(fulltextindexed=True)
    support_seda_exports = String(__permissions__={'read': ('managers', 'users', 'guests',),
                                                   'add': (),
                                                   'update': ()})


class seda_transferring_agent(RelationDefinition):  # XXX Agent use_profile Profile
    subject = 'SEDAProfile'
    object = 'Agent'
    cardinality = '**'
    constraints = [RQLConstraint('O archival_role R, R name "deposit"')]


@relative_write_permissions_of('object')
class _seda_parent(RelationDefinition):
    name = 'seda_parent'
    composite = fulltext_container = 'object'
    inlined = True


class seda_parent_attachement(_seda_parent):
    subject = 'ProfileDocument'
    object = 'ProfileArchiveObject'
    cardinality = '?*'


class seda_parent_documentunit(_seda_parent):
    subject = 'ProfileArchiveObject'
    object = ('ProfileArchiveObject', 'SEDAProfile')
    cardinality = '?*'


@relative_update_permissions_through(('seda_parent', 'subject'))
@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1..n')
class ProfileArchiveObject(EntityType):
    """Archive object of a SEDA profile. There may be zero to n archive object in a profile archive
    or archive object.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Element_ArchiveObject.htm#ArchiveObject

    Merged with Archive of a SEDA profile. There may be one to n archives in a profile.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Element_Archive.htm#Archive
    """


@relative_update_permissions_through(('seda_parent', 'subject'))
@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='0..n')
class ProfileDocument(EntityType):
    """Document of a SEDA profile. There may be zero to n documents in a profile archive or archive
    object.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Element_Document.htm#Document
    """


class seda_file_type_code(RelationDefinition):
    subject = 'ProfileDocument'
    object = 'SEDAFileTypeCode'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = True


class seda_character_set_code(RelationDefinition):
    subject = 'ProfileDocument'
    object = 'SEDACharacterSetCode'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = True


class seda_document_type_code(RelationDefinition):
    subject = 'ProfileDocument'
    object = 'SEDADocumentTypeCode'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = True


@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='0..1')
class SEDAFileTypeCode(EntityType):
    """File type code of a document profile

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_filetype_code_xsd_Element_FileTypeCode.htm#FileTypeCode
    """


@relative_write_permissions_of('subject')
class seda_file_type_code_value(RelationDefinition):
    subject = 'SEDAFileTypeCode'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_file_type_code", CR is CWRType')]


@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='0..1')
class SEDACharacterSetCode(EntityType):
    """Character set code of a document profile

    http://www.archivesdefrance.culture.gouv.fr/seda/api/UNECE_CharacterSetEncodingCode_40106_xsd_Simple_Type_clm60133_CharacterSetEncodingCodeContentType.htm#CharacterSetEncodingCodeContentType
    """


@relative_write_permissions_of('subject')
class seda_character_set_code_value(RelationDefinition):
    subject = 'SEDACharacterSetCode'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_character_set_code", CR is CWRType')]


@seda_profile_element()
class SEDADocumentTypeCode(EntityType):
    """Document type code for a SEDA Document Profile

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_documenttype_code_xsd_Simple_Type_DocumentTypeCodeType.htm#DocumentTypeCodeType
    """


@relative_write_permissions_of('subject')
class seda_document_type_code_value(RelationDefinition):
    subject = 'SEDADocumentTypeCode'
    object = 'Concept'
    cardinality = '1*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_document_type_code", CR is CWRType')]


@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='0..1')
class SEDAAppraisalRule(EntityType):
    u"""Appraisal rule (règle de sort final) of a SEDA profile.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Element_AppraisalRule.htm#AppraisalRule
    """


@seda_profile_element()
class SEDAAppraisalRuleDuration(EntityType):
    u"""Duration of a SEDAAppraisalRule

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Complex_Type_AppraisalRuleType.htm#AppraisalRuleType_Duration
    """


@seda_profile_element()
class SEDAAppraisalRuleCode(EntityType):
    u"""Code of a SEDAAppraisalRule ('conserver', 'detruire')

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Complex_Type_AppraisalRuleType.htm#AppraisalRuleType_Code
    """


class seda_appraisal_rule(RelationDefinition):
    subject = 'ProfileArchiveObject'
    object = 'SEDAAppraisalRule'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = True


class seda_appraisal_rule_duration(RelationDefinition):
    subject = 'SEDAAppraisalRule'
    object = 'SEDAAppraisalRuleDuration'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = True


class seda_appraisal_rule_duration_value(RelationDefinition):
    subject = 'SEDAAppraisalRuleDuration'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_appraisal_rule_duration", CR is CWRType')]


class seda_appraisal_rule_code(RelationDefinition):
    subject = 'SEDAAppraisalRule'
    object = 'SEDAAppraisalRuleCode'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = True


@relative_write_permissions_of('subject')
class seda_appraisal_rule_code_value(RelationDefinition):
    subject = 'SEDAAppraisalRuleCode'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_appraisal_rule_code", CR is CWRType')]


# XXX SEDA 1.0 stricto-sensu would be
#   ProfilArchive-[0..1]->AccessRestrictionRule-1->AccessRestrictionCode
#                                              -1->DateDepartCalcul
#
# but we skip AccessRestrictionRule entity for now as DateDepartCalcul isn't handled yet.
#
# Regarding cardinalities: AccessRestrictionRule is mandatory from archive but optional from archive
# object. This is problematic since the user cardinality is stored on the target entity.  To handle
# this while keeping this modelization, we allow on the target entity the most relaxed cardinalities
# (['0..1', '1']) and will handle restriction for the archive case in UI/hooks.
@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1')
class SEDAAccessRestrictionCode(EntityType):
    u"""Access resstriction code for an archive of a SEDA profile. There may be zero to one access
    control rule on an archive object but one and only one on an archive.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_accessrestriction_code_xsd_Element_AccessRestrictionCode.htm#AccessRestrictionCode
    """


class seda_access_restriction_code(RelationDefinition):
    subject = 'ProfileArchiveObject'
    object = 'SEDAAccessRestrictionCode'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = True


@relative_write_permissions_of('subject')
class seda_access_restriction_code_value(RelationDefinition):
    subject = 'SEDAAccessRestrictionCode'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_access_restriction_code", CR is CWRType')]


@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1')
class SEDAContentDescription(EntityType):
    u"""Content description for an archive or archive object of a SEDA profile. There may be zero to
    one content description on an archive object by one and only one on an archive.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Element_ContentDescription.htm#ContentDescription
    """


class seda_content_description(RelationDefinition):
    subject = 'ProfileArchiveObject'
    object = 'SEDAContentDescription'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = True


@seda_profile_element()
class SEDADescriptionLevel(EntityType):
    """Description level for a content description of a SEDA profile.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Complex_Type_ContentDescriptionType.htm#ContentDescriptionType_DescriptionLevel
    """


class seda_description_level(RelationDefinition):
    subject = 'SEDAContentDescription'
    object = 'SEDADescriptionLevel'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = True


@relative_write_permissions_of('subject')
class seda_description_level_value(RelationDefinition):
    subject = 'SEDADescriptionLevel'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation CR, CR name '
                                 '"seda_description_level", CR is CWRType')]


@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='0..n')
class SEDAKeyword(EntityType):
    """Keyword for a content description of a SEDA profile.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Complex_Type_ContentDescriptionType.htm#ContentDescriptionType_Keyword
    """


class seda_keyword_of(RelationDefinition):
    subject = 'SEDAKeyword'
    object = 'SEDAContentDescription'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True


@relative_write_permissions_of('subject')
class seda_keyword_scheme(RelationDefinition):
    subject = 'SEDAKeyword'
    object = 'ConceptScheme'
    cardinality = '1*'
    inlined = True


@relative_write_permissions_of('subject')
class seda_keyword_value(RelationDefinition):
    subject = 'SEDAKeyword'
    object = 'Concept'
    cardinality = '?*'
    inlined = True
    constraints = [
        RQLConstraint('S seda_keyword_scheme KS, O in_scheme KS',
                      msg=_("concept doesn't belong to the scheme associated to the keyword")),
    ]


@relative_update_permissions_through(('seda_oldest_date', 'object'),
                                     ('seda_latest_date', 'object'),
                                     may_not_exists=False)
@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='0..1')
class SEDADate(EntityType):
    """Date used in a SEDA profile."""
    value = Date()


@relative_write_permissions_of('subject')
class seda_oldest_date(RelationDefinition):
    subject = 'SEDAContentDescription'
    object = 'SEDADate'
    cardinality = '??'
    composite = fulltext_container = 'subject'
    inlined = True
    constraints = [
        RQLConstraint('NOT EXISTS(D seda_latest_date O)',
                      msg=_('SEDA date cannot be used as oldest and latest')),
    ]


@relative_write_permissions_of('subject')
class seda_latest_date(RelationDefinition):
    subject = 'SEDAContentDescription'
    object = 'SEDADate'
    cardinality = '??'
    composite = fulltext_container = 'subject'
    inlined = True
    constraints = [
        RQLConstraint('NOT EXISTS(D seda_oldest_date O)',
                      msg=_('SEDA date cannot be used as oldest and latest')),
    ]


@seda_profile_element()
class SEDAName(EntityType):
    """Name of an archive of a SEDA profile or profile object.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Complex_Type_ArchiveType.htm#ArchiveType_Name
    """
    value = String(fulltextindexed=True)


class seda_name(RelationDefinition):
    subject = 'ProfileArchiveObject'
    object = 'SEDAName'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = True


@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='0..1')
class SEDADescription(EntityType):
    """Description of a document of a SEDA profile. There may be zero to one description on a
    profile document.

    http://www.archivesdefrance.culture.gouv.fr/seda/api/seda_v1-0_archive_xsd_Complex_Type_DocumentType.htm#DocumentType_Description
    """
    value = String(fulltextindexed=True)  # XXX Rich String ?


class seda_description(RelationDefinition):
    subject = ('ProfileDocument', 'SEDAContentDescription')
    object = 'SEDADescription'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = True


class _seda_clone_of(RelationDefinition):  # XXX Profile clone_of Profile
    cardinality = '?*'
    inlined = True


class seda_clone_of_document(_seda_clone_of):
    name = 'seda_clone_of'
    subject = 'ProfileDocument'
    object = 'ProfileDocument'


class seda_clone_of_documentunit(_seda_clone_of):
    name = 'seda_clone_of'
    subject = 'ProfileArchiveObject'
    object = 'ProfileArchiveObject'


class scheme_relation(RelationDefinition):
    """Special relation from a concept scheme to a relation type, that may be used to restrict
    possible concept of a particular relation without depending on the scheme's name or other weak
    mecanism. See :class:`seda_access_restriction_code_value` for instance.
    """
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers',),
                       'delete': ('managers',)}
    subject = 'ConceptScheme'
    object = 'CWRType'
    cardinality = '*?'


class seda_replace(RelationDefinition):  # XXX Profile new_version_of Profile
    __permissions__ = {'read': ('managers', 'users', 'guests'),
                       'add': ('managers', 'users',
                               RRQLExpression('O in_state ST, ST name "published"')),
                       'delete': ()}
    subject = 'SEDAProfile'
    object = 'SEDAProfile'
    cardinality = '??'
    inlined = True


def post_build_callback(schema):
    for etype, graph in PERMISSIONS_GRAPHS.iteritems():
        graph_set_etypes_update_permissions(schema, graph(schema), etype)
        graph_set_write_rdefs_permissions(schema, graph(schema), etype)
    assert _RELATIVE_PERM_RELATIONS_CONSISTENCY_CHECK == OUTER_RELATIVE_PERM_RELATIONS, \
        ('inconsistency between calls to relative_permission_of and '
         'OUTER_RELATIVE_PERM_RELATIONS: %s' % _RELATIVE_PERM_RELATIONS_CONSISTENCY_CHECK)
    # permissions override
    schema['Label'].set_action_permissions('delete', ('managers', 'users'))
    for rtype in ('in_scheme', 'broader_concept', 'label_of'):
        for rdef in schema[rtype].rdefs.values():
            rdef.set_action_permissions('add', ('managers', 'users'))
            if rtype == 'label_of':
                rdef.set_action_permissions('delete', ('managers', 'users'))
