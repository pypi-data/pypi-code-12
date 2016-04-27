# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Collaborative Group implementation'''

from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import ICollaborativeGroup
from groupspace import GroupSpace, GroupSpaceSchema
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata
from zope.interface import implements

CollaborativeGroupSchema = GroupSpaceSchema.copy() + atapi.Schema((
    # No additional fields
))

schemata.finalizeATCTSchema(CollaborativeGroupSchema, folderish=True, moveDiscussion=False)

class CollaborativeGroup(GroupSpace):
    '''A collaborative group'''
    implements(ICollaborativeGroup)
    schema              = CollaborativeGroupSchema
    portal_type         = 'Collaborative Group'
    def getIndexPortalType(self):
        return 'Collaborative Group Index'

atapi.registerType(CollaborativeGroup, PROJECTNAME)
