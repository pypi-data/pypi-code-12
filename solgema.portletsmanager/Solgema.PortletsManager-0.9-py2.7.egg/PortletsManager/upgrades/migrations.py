import logging
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility, getAdapters, getMultiAdapter
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping, IPortletAssignmentSettings
from Solgema.PortletsManager.interfaces import ISolgemaPortletAssignment

def doNothing(context):
    pass

def reinstall(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.PortletsManager:default')

def upgrade06(context):
    portal_quickinstaller = getToolByName(context, 'portal_quickinstaller')
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.PortletsManager.upgrades:upgrade06')
    jstool = getToolByName(context, 'portal_javascripts')
    jstool.cookResources()
    csstool = getToolByName(context, 'portal_css')
    csstool.cookResources()

def upgrade08(context):
    portal_setup = getToolByName(context, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile('profile-Solgema.PortletsManager.upgrades:upgrade08')

def upgrade09(context):
    portal_setup = getToolByName(context, 'portal_setup')
    site = getToolByName(context, 'portal_url').getPortalObject()
    rcolumn = getUtility(IPortletManager, name="plone.rightcolumn", context=site)
    lcolumn = getUtility(IPortletManager, name="plone.leftcolumn", context=site)
    rmanager = getMultiAdapter((site, rcolumn), IPortletAssignmentMapping)
    lmanager = getMultiAdapter((site, lcolumn), IPortletAssignmentMapping)
    rportletnames = [v.title for v in rmanager.values()]
    lportletnames = [v.title for v in lmanager.values()]
    for portlet in rmanager.values():
        setattr(IPortletAssignmentSettings(portlet), 'stopUrls', getattr(ISolgemaPortletAssignment(portlet), 'stopUrls', []))
    for portlet in lmanager.values():
        setattr(IPortletAssignmentSettings(portlet), 'stopUrls', getattr(ISolgemaPortletAssignment(portlet), 'stopUrls', []))
    

