# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Group Space implementation'''

from edrnsite.collaborations import PackageMessageFactory as _
from edrnsite.collaborations.config import PROJECTNAME
from edrnsite.collaborations.interfaces import IGroupSpace
from plone.app.contentrules.rule import get_assignments
from plone.contentrules.engine.assignments import RuleAssignment
from plone.contentrules.engine.interfaces import IRuleAssignmentManager, IRuleStorage
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.interface import implements

GroupSpaceSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.BooleanField(
        'updateNotifications',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'Update Notifications'),
            description=_(u'Enable notifying members (by email) of updates to this group.'),
        ),
    ),
))
GroupSpaceSchema['title'].storage = atapi.AnnotationStorage()
GroupSpaceSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(GroupSpaceSchema, folderish=True, moveDiscussion=False)

class GroupSpace(folder.ATFolder):
    '''A group space'''
    implements(IGroupSpace)
    schema              = GroupSpaceSchema
    portal_type         = 'Group Space'
    description         = atapi.ATFieldProperty('description')
    title               = atapi.ATFieldProperty('title')
    updateNotifications = atapi.ATFieldProperty('updateNotifications')
    def getIndexPortalType(self):
        '''Return the portal_type of the index page that should be added to this group.
        Subclasses should override this with their own special index portal_type.'''
        return 'Group Space Index'

atapi.registerType(GroupSpace, PROJECTNAME)

def addContentRules(obj, event):
    '''For newly-created groups, add content rules to handle notifications and an index page.'''
    if not IGroupSpace.providedBy(obj): return
    factory = getToolByName(obj, 'portal_factory')
    if factory.isTemporary(obj): return
    # First, the index
    if obj.Title():
        if 'index_html' not in obj.keys():
            index = obj[obj.invokeFactory(obj.getIndexPortalType(), 'index_html')]
        else:
            index = obj['index_html']
        index.setTitle(obj.title)
        index.setDescription(obj.description)
        index.reindexObject()
        obj.setDefaultPage('index_html')
    # Now the content rules
    assignable, storage, path = IRuleAssignmentManager(obj), getUtility(IRuleStorage), '/'.join(obj.getPhysicalPath())
    for ruleName in ('gs-add-event', 'gs-mod-event', 'gs-pub-event'):
        if ruleName not in assignable and ruleName in storage:
            assignable[ruleName] = RuleAssignment(ruleName)
            get_assignments(storage[ruleName]).insert(path)
