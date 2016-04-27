# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from Acquisition import aq_base
from eke.biomarker.testing import EKE_BIOMARKER_FIXTURE
from eke.knowledge.testing import EKE_KNOWLEDGE_FIXTURE
from eke.study.testing import EKE_STUDY_FIXTURE
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from plone.testing import z2
from Products.CMFCore.utils import getToolByName
from Products.MailHost.interfaces import IMailHost
from zope.component import getMultiAdapter, getSiteManager
from zope.component import getUtility
from zope.publisher.browser import TestRequest

_sentMessages = []

class _TestingMailHost(object):
    smtp_queue = True
    def __init__(self):
        self.resetSentMessages()
    def send(self, message, mto=None, mfrom=None, subject=None, encode=None, immediate=False, charset=None, msg_type=None):
        global _sentMessages
        _sentMessages.append(message)
    def resetSentMessages(self):
        global _sentMessages
        _sentMessages = []
    def getSentMessages(self):
        global _sentMessages
        return _sentMessages
    def getId(self):
        return 'MailHost'


_testingMailHost = _TestingMailHost()

class EDRNSiteCollaborations(PloneSandboxLayer):
    defaultBases = (EKE_KNOWLEDGE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import edrnsite.collaborations
        self.loadZCML(package=edrnsite.collaborations)
        z2.installProduct(app, 'edrnsite.collaborations')
        import eke.publications
        self.loadZCML(package=eke.publications)
        z2.installProduct(app, 'eke.publications')
        import eke.site
        self.loadZCML(package=eke.site)
        z2.installProduct(app, 'eke.site')
        import eke.biomarker
        self.loadZCML(package=eke.biomarker)
        z2.installProduct(app, 'eke.biomarker')
        import eke.study
        self.loadZCML(package=eke.study)
        z2.installProduct(app, 'eke.study')
        import eke.ecas
        self.loadZCML(package=eke.ecas)
        z2.installProduct(app, 'eke.ecas')
        # You'd think this would be included in the Plone fixture:
        import plone.stringinterp
        self.loadZCML(package=plone.stringinterp)
    def _setupTestContent(self, portal):
        from eke.biomarker.tests.base import registerLocalTestData
        registerLocalTestData()
        organs = portal[portal.invokeFactory(
            'Knowledge Folder', 'basic-body-systems', title=u'Organs', rdfDataSource=u'testscheme://localhost/bodysystems/b'
        )]
        resources = portal[portal.invokeFactory(
            'Knowledge Folder', 'basic-resources', title=u'Resources', rdfDataSource=u'testscheme://localhost/resources/b'
        )]
        protocols = portal[portal.invokeFactory(
            'Study Folder', 'protocols', title=u'Protocols', rdfDataSource=u'testscheme://localhost/protocols/a'
        )]
        biomarkers = portal[portal.invokeFactory(
            'Biomarker Folder', 'biomarkers', title=u'Biomarkers', rdfDataSource=u'testscheme://localhost/biomarkers/a',
            bmoDataSource=u'testscheme://localhost/biomarkerorgans/a', bmuDataSource=u'testscheme://localhost/biomuta/a',
            bmSumDataSource=u'testscheme://localhost/summary/a',
        )]
        datasets = portal[portal.invokeFactory(
            'Dataset Folder', 'datasets', title=u'Datasets', rdfDataSource=u'testscheme://localhost/datasets/a',
        )]
        sites = portal[portal.invokeFactory(
            'Site Folder', 'sites', title=u'Sites',
            rdfDataSource=u'testscheme://localhost/sites/d', peopleDataSource=u'testscheme://localhost/people/many'
        )]
        for folder in (organs, resources, sites, protocols, biomarkers, datasets):
            ingestor = getMultiAdapter((folder, TestRequest()), name=u'ingest')
            ingestor.render = False
            ingestor()
        protocol = protocols['ps-public-safety']
        protocol.project = True
        protocol.setLeadInvestigatorSite(sites['5d-were-marked-up'])
        protocol.reindexObject(idxs=['project'])
        protocol2 = protocols[protocols.invokeFactory('Protocol', 'p2', title=u'Protocol Two')]
        protocol2.reindexObject()
        protocol3 = protocols[protocols.invokeFactory('Protocol', 'p3', title=u'Protocol Three')]
        protocol3.reindexObject()
        for i in xrange(0, 8):
            dataset = datasets[datasets.invokeFactory('Dataset', 'd%d' % i, title=u'Dataset %d' % i)]
            if i > 2:
                if i % 2 == 0:
                    dataset.setProtocol(protocol2)
                else:
                    dataset.setProtocol(protocol3)
            dataset.reindexObject()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'edrnsite.collaborations:default')
        wfTool = getToolByName(portal, 'portal_workflow')
        wfTool.setDefaultChain('plone_workflow')
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        self._setupTestContent(portal)
        portal._original_MailHost = portal.MailHost
        portal.MailHost = _testingMailHost
        siteManager = getSiteManager(portal)
        siteManager.unregisterUtility(provided=IMailHost)
        siteManager.registerUtility(_testingMailHost, provided=IMailHost)
        portal._setPropValue('email_from_address', u'edrn-ic@jpl.nasa.gov')
        portal._setPropValue('email_from_name', u'EDRN Informatics Center')
        # Enable comments
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
    def tearDownPloneSite(self, portal):
        portal.MailHost = portal._original_MailHost
        siteManager = getSiteManager(portal)
        siteManager.unregisterUtility(provided=IMailHost)
        siteManager.registerUtility(aq_base(portal._original_MailHost), IMailHost)
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'edrnsite.collaborations')
    
EDRNSITE_COLLABORATIONS_FIXTURE = EDRNSiteCollaborations()
EDRNSITE_COLLABORATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EDRNSITE_COLLABORATIONS_FIXTURE,),
    name='EDRNSiteCollaborations:Integration',
)
EDRNSITE_COLLABORATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EDRNSITE_COLLABORATIONS_FIXTURE,),
    name='EDRNSiteCollaborations:Functional',
)
