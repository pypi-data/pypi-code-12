from plone.app.caching.interfaces import IETagValue
from zope.component import adapts
from zope.component.hooks import getSite
from zope.interface import implements
from zope.interface import Interface


class EditModeEtag(object):
    implements(IETagValue)
    adapts(Interface, Interface)

    def __init__(self, published, request):
        self.published = published
        self.request = request

    def __call__(self):
        switcher = getSite().restrictedTraverse('@@switch-editmode')
        return switcher.get_state()
