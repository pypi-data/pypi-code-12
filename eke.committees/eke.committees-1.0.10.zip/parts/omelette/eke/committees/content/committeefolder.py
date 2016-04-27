# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Committee folder.'''

from eke.knowledge.content import knowledgefolder
from eke.committees.config import PROJECTNAME
from eke.committees.interfaces import ICommitteeFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from eke.committees import ProjectMessageFactory as _

CommitteeFolderSchema = knowledgefolder.KnowledgeFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        'siteSumDataSource',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Committee Summary Statistics Data Source'),
            description=_(u'URL to a source of summary statistics json that describes committee data.'),
            size=60,
        ),
    ),
    atapi.StringField(
        'dataSummary',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Committee Summary Statistics Data'),            description=_(u'Summary statistics json that describes committee data.'),
            size=10000,
        ),
    ),
))

finalizeATCTSchema(CommitteeFolderSchema, folderish=True, moveDiscussion=False)

class CommitteeFolder(knowledgefolder.KnowledgeFolder):
    '''Committee Folder which contains Committees.'''
    implements(ICommitteeFolder)
    portal_type = 'Committee Folder'
    schema      = CommitteeFolderSchema
    siteSumDataSource = atapi.ATFieldProperty('siteSumDataSource')
    dataSummary       = atapi.ATFieldProperty('dataSummary')

atapi.registerType(CommitteeFolder, PROJECTNAME)
