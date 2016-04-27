# encoding: utf-8
# Copyright 2011—2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Site Collaborations: collaborative group index view
'''

from Acquisition import aq_inner, aq_parent
from edrnsite.collaborations.interfaces import IHighlight
from groupspaceindex import GroupSpaceIndexView
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

def getHighlights(context, review_state=None):
    catalog = getToolByName(context, 'portal_catalog')
    criteria = dict(
        object_provides=IHighlight.__identifier__,
        path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
        sort_on='modified',
        sort_order='reverse',
    )
    if review_state:
        criteria['review_state'] = review_state
    results = catalog(**criteria)
    return [dict(title=i.Title, description=i.Description, url=i.getURL(), brain=i) for i in results]


class CollaborativeGroupIndexView(GroupSpaceIndexView):
    '''Default view for a Collaborative Group Index.'''
    index = ViewPageTemplateFile('templates/collaborativegroupindex.pt')
    def __call__(self):
        return self.index()
    @memoize
    def topHighlights(self):
        context = aq_parent(aq_inner(self.context))
        return getHighlights(context, 'published')[0:self.numTops()]
    @memoize
    def topProjects(self):
        context = aq_inner(self.context)
        return context.projects[0:self.numTops()]
    @memoize
    def numHighlights(self):
        context = aq_parent(aq_inner(self.context))
        return len(getHighlights(context))
    @memoize
    def numProjects(self):
        context = aq_inner(self.context)
        return len(context.projects)
    def projects(self):
        projects = aq_inner(self.context).projects
        projects.sort(lambda a, b: cmp(a.title, b.title))
        return projects
    def protocols(self):
        protocols = aq_inner(self.context).protocols
        protocols.sort(lambda a, b: cmp(a.title, b.title))
        return protocols
    def datasets(self):
        datasets = aq_inner(self.context).datasets
        byProtocol, noProtocol = {}, []
        for dataset in datasets:
            protocol = dataset.protocol
            if not protocol:
                noProtocol.append(dataset)
            else:
                if protocol not in byProtocol:
                    byProtocol[protocol] = []
                byProtocol[protocol].append(dataset)
        byProtocol = byProtocol.items()
        byProtocol.sort(lambda a, b: cmp(a[0].title, b[0].title))
        noProtocol.sort(lambda a, b: cmp(a.title, b.title))
        return byProtocol, noProtocol


class CollaborativeGroupHighlightsView(BrowserView):
    '''Highlights-only view for a Collaborative Group Index.'''
    index = ViewPageTemplateFile('templates/collaborativegrouphighlights.pt')
    def __call__(self):
        return self.index()
    @memoize
    def highlights(self):
        context = aq_parent(aq_inner(self.context))
        return getHighlights(context)
    def haveHighlights(self):
        return len(self.highlights()) > 0


