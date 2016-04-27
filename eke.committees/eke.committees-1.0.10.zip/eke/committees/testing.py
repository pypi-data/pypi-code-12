# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from Acquisition import aq_base
from edrnsite.collaborations.testing import EDRNSITE_COLLABORATIONS_FIXTURE
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting
from plone.testing import z2
from Products.MailHost.interfaces import IMailHost
from zope.component import getSiteManager
import eke.knowledge.tests.base as ekeKnowledgeBase
import eke.site.tests.base as ekeSiteBase

_twoCommitteesRDF = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:_3='http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#' xmlns:_4='http://purl.org/dc/terms/' 
    xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
  <rdf:Description rdf:about='http://usa.gov/data/committees/1'>
    <rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#Committee'/>
    <_4:title>Appropriations</_4:title>
    <_3:abbreviatedName>App</_3:abbreviatedName>
    <_3:committeeType>Committee</_3:committeeType>
    <_3:chair rdf:resource='http://pimpmyho.com/data/registered-person/3'/>
    <_3:coChair rdf:resource='http://pimpmyho.com/data/registered-person/1'/>
    <_3:consultant rdf:resource='http://pimpmyho.com/data/registered-person/3'/>
    <_3:member rdf:resource='http://pimpmyho.com/data/registered-person/3'/>
    <_3:member rdf:resource='http://pimpmyho.com/data/registered-person/2'/>
  </rdf:Description>
  <rdf:Description rdf:about='http://edrn.nci.nih.gov/data/committees/2'>
    <rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#Committee'/>
    <_4:title>Ways and Means</_4:title>
    <_3:committeeType>Committee</_3:committeeType>
  </rdf:Description>
</rdf:RDF>'''

_threeCommitteesRDF = '''<?xml version='1.0' encoding='UTF-8'?>
<rdf:RDF xmlns:_3='http://edrn.nci.nih.gov/xml/rdf/edrn.rdf#' xmlns:_4='http://purl.org/dc/terms/' 
    xmlns:rdf='http://www.w3.org/1999/02/22-rdf-syntax-ns#'>
  <rdf:Description rdf:about='http://usa.gov/data/committees/1'>
    <rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#Committee'/>
    <_4:title>Appropriations</_4:title>
    <_3:abbreviatedName>App</_3:abbreviatedName>
    <_3:committeeType>Committee</_3:committeeType>
    <_3:chair rdf:resource='http://pimpmyho.com/data/registered-person/3'/>
    <_3:coChair rdf:resource='http://pimpmyho.com/data/registered-person/1'/>
    <_3:consultant rdf:resource='http://pimpmyho.com/data/registered-person/3'/>
    <_3:member rdf:resource='http://pimpmyho.com/data/registered-person/3'/>
    <_3:member rdf:resource='http://pimpmyho.com/data/registered-person/2'/>
  </rdf:Description>
  <rdf:Description rdf:about='http://usa.gov/data/committees/2'>
    <rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#Committee'/>
    <_4:title>Ways and Means</_4:title>
    <_3:committeeType>Committee</_3:committeeType>
  </rdf:Description>
  <rdf:Description rdf:about='http://usa.gov/data/committees/3'>
    <rdf:type rdf:resource='http://edrn.nci.nih.gov/rdf/types.rdf#Committee'/>
    <_4:title>Science and Technology</_4:title>
    <_3:committeeType>Committee</_3:committeeType>
  </rdf:Description>
</rdf:RDF>'''

_summaryCommitteesJSON = '''{"member":{"G.I. and Other Associated Cancers Research Group":27,"Lung and Upper Aerodigestive Cancers Research Group":20,"Prostate and Urologic Cancers Research Group":18,"Breast and Gynecologic Cancers Research Group":27},"protocol":{"G.I. and Other Associated Cancers Research Group":62,"Lung and Upper Aerodigestive Cancers Research Group":25,"Prostate and Urologic Cancers Research Group":56},"data":{"G.I. and Other Associated Cancers Research Group":2,"Lung and Upper Aerodigestive Cancers Research Group":35,"Prostate and Urologic Cancers Research Group":23,"Breast and Gynecologic Cancers Research Group":5},"biomarker":{"Lung and Upper Aerodigestive Cancers Research Group":33,"Prostate and Urologic Cancers Research Group":5,"Breast and Gynecologic Cancers Research Group":181},"panel":{"Lung and Upper Aerodigestive Cancers Research Group":12,"Breast and Gynecologic Cancers Research Group":2}}'''

class _TestingMailHost(object):
    smtp_queue = True
    _sentMessages = []
    def __init__(self):
        self.resetSentMessages()
    def send(self, message, mto=None, mfrom=None, subject=None, encode=None, immediate=False, charset=None, msg_type=None):
        self._sentMessages.append(message)
    def resetSentMessages(self):
        self._sentMessages = []
    def getSentMessages(self):
        return self._sentMessages
    def getId(self):
        return 'MailHost'

class EKECommittees(PloneSandboxLayer):
    defaultBases = (EDRNSITE_COLLABORATIONS_FIXTURE,)
    def _createTestingMailHost(self):
        self._testingMailHost = _TestingMailHost()
    def setUpZope(self, app, configurationContext):
        import eke.committees
        self.loadZCML(package=eke.committees)
        z2.installProduct(app, 'eke.committees')
        ekeSiteBase.registerLocalTestData()
        ekeKnowledgeBase.registerTestData('/committees/a', _twoCommitteesRDF)
        ekeKnowledgeBase.registerTestData('/committees/b', _threeCommitteesRDF)
        ekeKnowledgeBase.registerTestData('/summary/a', _summaryCommitteesJSON)
        self._createTestingMailHost()
        import plone.stringinterp
        self.loadZCML(package=plone.stringinterp)
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.committees:default')
        portal._original_MailHost = portal.MailHost
        portal.MailHost = self._testingMailHost
        siteManager = getSiteManager(portal)
        siteManager.unregisterUtility(provided=IMailHost)
        siteManager.registerUtility(self._testingMailHost, provided=IMailHost)
        portal._setPropValue('email_from_address', u'edrn-ic@jpl.nasa.gov')
        portal._setPropValue('email_from_name', u'EDRN Informatics Center')
    def tearDownPloneSite(self, portal):
        portal.MailHost = portal._original_MailHost
        siteManager = getSiteManager(portal)
        siteManager.unregisterUtility(provided=IMailHost)
        siteManager.registerUtility(aq_base(portal._original_MailHost), IMailHost)
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'eke.committees')

EKE_COMMITTEES_FIXTURE = EKECommittees()
EKE_COMMITTEES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_COMMITTEES_FIXTURE,),
    name='EKECommittees:Integration',
)
EKE_COMMITTEES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_COMMITTEES_FIXTURE,),
    name='EKECommittees:Functional',
)
