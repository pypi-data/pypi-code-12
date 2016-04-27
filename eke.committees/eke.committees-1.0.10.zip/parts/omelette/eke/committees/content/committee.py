# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Committee.'''

from eke.knowledge import dublincore
from eke.knowledge.content import knowledgeobject
from eke.committees import ProjectMessageFactory as _
from eke.committees.config import PROJECTNAME
from eke.committees.interfaces import ICommittee
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

CommitteeSchema = knowledgeobject.KnowledgeObjectSchema.copy() + atapi.Schema((
    atapi.StringField(
        'abbreviatedName',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Abbreviated Name'),
            description=_(u'A shorter name for this committee.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#abbreviatedName',
    ),
    atapi.StringField(
        'committeeType',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Committee Type'),
            description=_(u'What kind of committee this is.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#committeeType',
    ),
    atapi.ReferenceField(
        'chair',
        required=False,
        enforceVocabulary=True,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        relationship='chairsOfThisCommittee',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.People',
        widget=atapi.ReferenceWidget(
            label=_(u'Chairs'),
            description=_(u'Chairpeople of this committee.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#chair',
    ),
    atapi.ReferenceField(
        'coChair',
        required=False,
        enforceVocabulary=True,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        relationship='coChairsOfThisCommittee',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.People',
        widget=atapi.ReferenceWidget(
            label=_(u'Co-Chairs'),
            description=_(u'Co-Chairpeople of this committee.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#coChair',
    ),
    atapi.ReferenceField(
        'consultant',
        required=False,
        enforceVocabulary=True,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        relationship='consultantsToThisCommittee',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.People',
        widget=atapi.ReferenceWidget(
            label=_(u'Consultants'),
            description=_(u'Consultants to this committee.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#consultant',
    ),
    atapi.ReferenceField(
        'member',
        required=False,
        enforceVocabulary=True,
        multiValued=True,
        storage=atapi.AnnotationStorage(),
        relationship='membersOfThisCommittee',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.People',
        widget=atapi.ReferenceWidget(
            label=_(u'Members'),
            description=_(u'Members of this committee.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#member',
    ),
))
# FIXME: KnowledgeObjectSchema has title's predicate set to something wrong.
# When that's finally fixed, remove this line:
CommitteeSchema['title'].predicateURI = dublincore.TITLE_URI

finalizeATCTSchema(CommitteeSchema, folderish=False, moveDiscussion=False)

class Committee(knowledgeobject.KnowledgeObject):
    '''Committee.'''
    implements(ICommittee)
    schema          = CommitteeSchema
    portal_type     = 'Committee'
    abbreviatedName = atapi.ATFieldProperty('abbreviatedName')
    chair           = atapi.ATReferenceFieldProperty('chair')
    coChair         = atapi.ATReferenceFieldProperty('coChair')
    consultant      = atapi.ATReferenceFieldProperty('consultant')
    member          = atapi.ATReferenceFieldProperty('member')
    committeeType   = atapi.ATFieldProperty('committeeType')

atapi.registerType(Committee, PROJECTNAME)
