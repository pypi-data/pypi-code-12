# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from pkg_resources import resource_filename
from plone.app.ldap.engine.interfaces import ILDAPConfiguration
from plone.app.ldap.engine.schema import LDAPProperty
from plone.app.ldap.engine.server import LDAPServer
from plone.app.ldap.ploneldap.util import guaranteePluginExists
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zope.component import getUtility, ComponentLookupError

def publish(item, wfTool=None):
    if wfTool is None:
        wfTool = getToolByName(item, 'portal_workflow')
    try:
        wfTool.doActionFor(item, action='publish')
        item.reindexObject()
    except WorkflowException:
        pass
    if IFolderish.providedBy(item):
        for itemID, subItem in item.contentItems():
            publish(subItem, wfTool)


def setUpHomePage(portal):
    if 'front-page' not in portal.keys(): return
    frontPage = portal['front-page']
    frontPage.setExcludeFromNav(True)
    frontPage.setPresentation(False)
    portal.setDefaultPage('front-page')
    publish(portal['front-page'])
    frontPage.reindexObject()
    

def loadPhotographs(portal):
    if 'staff-photographs' in portal.keys(): return
    portal._importObjectFromFile(resource_filename(__name__, 'data/staff-photographs.zexp'))
    publish(portal['staff-photographs'])


def setupLDAP(portal):
    qi = getToolByName(portal, 'portal_quickinstaller')
    if not qi.isProductInstalled('plone.app.ldap'):
        qi.installProduct('plone.app.ldap')
    try:
        ldapConfig = getUtility(ILDAPConfiguration)
    except ComponentLookupError:
        return
    if ldapConfig.user_object_classes == 'edrnPerson':
        return
    ldapConfig.user_object_classes = 'edrnPerson'
    ldapConfig.ldap_type = u'LDAP'
    ldapConfig.user_scope = 1
    ldapConfig.user_base = 'dc=edrn,dc=jpl,dc=nasa,dc=gov'
    for i in ldapConfig.servers.keys():
        del ldapConfig.servers[i]
    ldapConfig.servers['ldapserver-1'] = LDAPServer(
        'edrn.jpl.nasa.gov', connection_type=1, connection_timeout=5, operation_timeout=15, enabled=True
    )
    p = ldapConfig.schema['uid']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'uid', '', u'User ID', False
    p = ldapConfig.schema['mail']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'mail', 'email', u'Email Address', False
    p = ldapConfig.schema['cn']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'cn', 'fullname', u'Full Name', False
    p = ldapConfig.schema['sn']
    p.ldap_name, p.plone_name, p.description, p.multi_valued = 'sn', '', u'Surname', False
    ldapConfig.schema['description'] = LDAPProperty('description', 'description', u'Description', False)
    ldapConfig.userid_attribute = 'uid'
    ldapConfig.rdn_attribute = 'uid'
    ldapConfig.login_attribute = 'uid'
    ldapConfig.group_scope = 1
    ldapConfig.group_base = 'dc=edrn,dc=jpl,dc=nasa,dc=gov'
    ldapConfig.bind_password = '70ve4edrn!'
    ldapConfig.bind_dn = 'uid=admin,ou=system'
    guaranteePluginExists()


def setupVarious(context):
    if context.readDataFile('edrndmcc.appserver.marker.txt') is None: return
    portal = context.getSite()
    setUpHomePage(portal)
    loadPhotographs(portal)
    # FIXME: Makes things super slow, why?
    # setupLDAP(portal)
