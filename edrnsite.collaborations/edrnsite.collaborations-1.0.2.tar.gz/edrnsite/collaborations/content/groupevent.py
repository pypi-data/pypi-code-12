# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.


'''Group Event implementation'''

from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import IGroupEvent
from Products.Archetypes import atapi
from Products.ATContentTypes.content import schemata, folder, event
from zope.interface import implements

GroupEventSchema = folder.ATFolderSchema.copy() + event.ATEventSchema.copy() + atapi.Schema((
    # Nothing else needed for now
))

schemata.finalizeATCTSchema(GroupEventSchema, folderish=True, moveDiscussion=True)
# finalizeATCTSchema moves 'location' into 'categories', we move it back:
GroupEventSchema.changeSchemataForField('location', 'default')
GroupEventSchema.moveField('location', before='startDate')

class GroupEvent(folder.ATFolder):
    '''A group event'''
    implements(IGroupEvent)
    schema         = GroupEventSchema
    archetype_name = 'Group Event'
    portal_type    = 'Group Event'

atapi.registerType(GroupEvent, PROJECTNAME)
