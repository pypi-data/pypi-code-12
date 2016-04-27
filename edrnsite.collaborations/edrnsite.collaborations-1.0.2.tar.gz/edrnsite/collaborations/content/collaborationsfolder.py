# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Collaborations Folder implementation'''

from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import ICollaborationsFolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from zope.interface import implements

CollaborationsFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    # No other fields at this time.
))
CollaborationsFolderSchema['title'].storage = atapi.AnnotationStorage()
CollaborationsFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(CollaborationsFolderSchema, folderish=True, moveDiscussion=False)

class CollaborationsFolder(folder.ATFolder):
    '''A folder for Collaborative Groups'''
    implements(ICollaborationsFolder)
    schema      = CollaborationsFolderSchema
    portal_type = 'Collaborations Folder'
    description = atapi.ATFieldProperty('description')
    title       = atapi.ATFieldProperty('title')

atapi.registerType(CollaborationsFolder, PROJECTNAME)
