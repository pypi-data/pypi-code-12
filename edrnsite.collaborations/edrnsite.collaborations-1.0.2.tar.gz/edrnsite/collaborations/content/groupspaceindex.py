# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Group space index implementation'''

from edrnsite.collaborations import PackageMessageFactory as _
from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import IGroupSpaceIndex
from Products.Archetypes import atapi
from Products.ATContentTypes.content import base, schemata
from zope.interface import implements

GroupSpaceIndexSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'chair',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=False,
        vocabulary_factory=u'eke.site.People',
        relationship='chairOfThisGroup',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Chair'),
            description=_(u'The person in charge of this group.'),
        )
    ),
    atapi.ReferenceField(
        'coChair',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=False,
        vocabulary_factory=u'eke.site.People',
        relationship='coChairOfThisGroup',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Co-Chair'),
            description=_(u'The assistant to the person in charge of this group.'),
        )
    ),
    atapi.ReferenceField(
        'members',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.site.People',
        relationship='membersOfThisGroup',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            title=_(u'Members'),
            description=_(u'Members of this group.'),
        )
    ),
))
GroupSpaceIndexSchema['title'].storage = atapi.AnnotationStorage()
GroupSpaceIndexSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(GroupSpaceIndexSchema, folderish=False, moveDiscussion=True)

class GroupSpaceIndex(base.ATCTContent):
    '''A group space'''
    implements(IGroupSpaceIndex)
    schema      = GroupSpaceIndexSchema
    portal_type = 'Group Space Index'
    chair       = atapi.ATReferenceFieldProperty('chair')
    coChair     = atapi.ATReferenceFieldProperty('coChair')
    description = atapi.ATFieldProperty('description')
    members     = atapi.ATReferenceFieldProperty('members')
    title       = atapi.ATFieldProperty('title')

atapi.registerType(GroupSpaceIndex, PROJECTNAME)
