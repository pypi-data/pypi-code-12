# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Site Collaborations: group space index view
'''

from edrnsite.collaborations.config import ADD_PERMISSIONS
from Acquisition import aq_inner, aq_parent
from plone.memoize.instance import memoize
from Products.ATContentTypes.interface import IATDocument, IATFile, IATImage, IATFolder, IATEvent
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from DateTime import DateTime
import urllib

_top = 3
_eventType = 'Group Event'
_eventAddPerm = ADD_PERMISSIONS[_eventType]

class GroupSpaceIndexView(BrowserView):
    '''Default view for a Group Space Index.'''
    index = ViewPageTemplateFile('templates/groupspaceindex.pt')
    def getAddableContent(self):
        '''Get the addable content types.  Subclasses can override.  Must return a mapping of type ID to
        a tuple of (permission name, portal type name, and true/false confusing flag).'''
        # This mapping goes from an addable content type ID (event, file, image, page) to a tuple identifying:
        # * The permission name to add an item of that type. Users must have that permission to add it.
        # * The name of the type according to the portal_types system.
        # * A flag indicating if such a type is confusing. Dan believes that users will find find adding
        #   plain old wiki-style HTML pages and images upsetting. So we automatically hide such confusing
        #   buttons. The tyranny of closed Micro$oft formats continues.
        # BTW: Why aren't these permission names defined as constants somewhere in ATContentTypes?
        return {
            # Add type   Permission name                    Type name       Confusing?
            'event':    (_eventAddPerm,                     _eventType,     False),
            'file':     ('ATContentTypes: Add File',        'File',         False),
            'image':    ('ATContentTypes: Add Image',       'Image',        True),
            'page':     ('ATContentTypes: Add Document',    'Document',     True),
            'folder':   ('ATContentTypes: Add Folder',      'Folder',       False),
        }
    def __call__(self):
        return self.index()
    def numTops(self):
        return _top
    def facebookURL(self):
        context = aq_parent(aq_inner(self.context))
        return u'http://facebook.com/sharer.php?' + urllib.urlencode(dict(t=context.title, u=context.absolute_url()))
    def twitterURL(self):
        context = aq_parent(aq_inner(self.context))
        return u'http://twitter.com/share?' + urllib.urlencode(dict(text=context.title, url=context.absolute_url()))
    @memoize
    def topEvents(self):
        return self.currentEvents()[0:self.numTops()]
    @memoize
    def numEvents(self):
        return len(self.currentEvents())
    def haveEvents(self):
        return len(self.currentEvents()) > 0
    def havePastEvents(self):
        return len(self.pastEvents()) > 0
    @memoize
    def currentEvents(self):
        return self._getEvents(end={'query': DateTime(), 'range': 'min'})
    @memoize
    def pastEvents(self):
        return self._getEvents(end={'query': DateTime(), 'range': 'max'})
    def _getEvents(self, **criteria):
        context = aq_parent(aq_inner(self.context))
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=IATEvent.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='start',
            **criteria)
        return [dict(title=i.Title, description=i.Description, start=i.start, url=i.getURL()) for i in results]
    @memoize
    def membersColumns(self):
        members = aq_inner(self.context).members
        members.sort(lambda a, b: cmp(a.title, b.title))
        half = len(members)/2 + 1
        left, right = members[:half], members[half:]
        return left, right
    def showNewButton(self, buttonType):
        addableContent = self.getAddableContent()
        if buttonType not in addableContent: return False
        context = aq_parent(aq_inner(self.context))
        mtool = getToolByName(context, 'portal_membership')
        perm = mtool.checkPermission(addableContent[buttonType][0], context)
        return perm and not addableContent[buttonType][2]
    def newButtonLink(self, buttonType):
        addableContent = self.getAddableContent()
        return aq_parent(aq_inner(self.context)).absolute_url() + '/createObject?type_name=' + addableContent[buttonType][1]
    def haveDocument(self):
        return len(self.documents()) > 0
    @memoize
    def documents(self):
        context = aq_parent(aq_inner(self.context))
        contentFilter = dict(object_provides=[i.__identifier__ for i in (IATDocument, IATImage, IATFile, IATFolder)])
        results = context.getFolderContents(contentFilter=contentFilter)
        # For some reason Highlights are being returned in the results, even though they don't provide any of the interfaces.
        results = [i for i in results if i.portal_type != 'Highlight']
        return results
