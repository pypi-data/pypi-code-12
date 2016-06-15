# -*- coding: utf-8 -*-

from zope import interface
from Products.CMFCore.utils import getToolByName
from redturtle.smartlink.interfaces import ISmartLinked

try:
    from plone.app.referenceablebehavior.interfaces import IReferenceable
    HAS_DX_REFS = True
except ImportError:
    HAS_DX_REFS = False


def smartLink(object, event):
    """
    Mark target object as ISmartLinked
    """
    target = object.getInternalLink()
    if target and not ISmartLinked.providedBy(target):
        interface.alsoProvides(target, ISmartLinked)
        target.reindexObject(['object_provides'])


def keepLink(object, event):
    """
    ISmartLinked object has been modified/renamed.
    We need to catalog/update all ISmartLinks referencing it
    """
    if HAS_DX_REFS:
        adapter = IReferenceable(object)
        backRefs = adapter.getBackReferences(relationship='internal_page')
    else:
        rcatalog = getToolByName(object, 'reference_catalog')
        backRefs = rcatalog.getBackReferences(object, relationship='internal_page')
    for r in backRefs:
        r.setRemoteUrl(r.getRemoteUrl())
        r.reindexObject()


def cleanSmartLinked(object, event):
    """
    Remove marker interface from a smart linked object when the Smart Link is removed
    """
    if object.getInternalLinkPath():
        linked = object.restrictedTraverse(object.getInternalLinkPath(), default=None)
        if linked:
            interface.noLongerProvides(linked, ISmartLinked)
