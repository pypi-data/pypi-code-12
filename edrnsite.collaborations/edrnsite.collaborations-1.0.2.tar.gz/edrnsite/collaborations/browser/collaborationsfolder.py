# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Site Collaborations: collaborations folder view
'''

from Acquisition import aq_inner
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class CollaborationsFolderView(BrowserView):
    '''Default view for a Collaborations Folder.'''
    __call__ = ViewPageTemplateFile('templates/collaborationsfolder.pt')
    def haveCollaborativeGroups(self):
        return len(self.collaborativeGroups()) > 0
    def haveGroupSpaces(self):
        return len(self.groupSpaces()) > 0
    def _getGroups(self, portal_type):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            portal_type=portal_type,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in results]
    @memoize
    def collaborativeGroups(self):
        return self._getGroups('Collaborative Group')
    @memoize
    def groupSpaces(self):
        return self._getGroups('Group Space')
