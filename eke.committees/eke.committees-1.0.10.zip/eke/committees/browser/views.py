# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Committees: views for content types.
'''

from Acquisition import aq_inner
from eke.committees.interfaces import ICommittee, ICommitteeFolder
from eke.knowledge.browser.views import KnowledgeFolderView, KnowledgeObjectView
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from edrnsite.collaborations.interfaces import IGroupSpace
from Products.Five.browser import BrowserView

class CommitteeFolderView(KnowledgeFolderView):
    '''Default view of a Committee Folder.'''
    __call__ = ViewPageTemplateFile('templates/committeefolder.pt')
    def haveCommittees(self):
        return len(self.committees()) > 0
    def haveSubfolders(self):
        return len(self.subfolders()) > 0
    @memoize
    def committees(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=(ICommittee.__identifier__, IGroupSpace.__identifier__),
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, url=i.getURL()) for i in results]
    @memoize
    def subfolders(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ICommitteeFolder.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in results]

class CommitteeView(KnowledgeObjectView):
    '''Default view of a Committee.'''
    __call__ = ViewPageTemplateFile('templates/committee.pt')

class CommitteeFolderSummary(BrowserView):
    def __call__(self):
        self.request.RESPONSE.setHeader('Content-type', 'application/json')
        context = aq_inner(self.context)
        return context.dataSummary
