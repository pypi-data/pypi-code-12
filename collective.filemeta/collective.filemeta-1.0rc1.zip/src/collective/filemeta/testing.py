# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.filemeta


class CollectiveDocumentfileLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.filemeta)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.filemeta:exampletype')


COLLECTIVE_DOCUMENTFILE_FIXTURE = CollectiveDocumentfileLayer()


COLLECTIVE_DOCUMENTFILE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_DOCUMENTFILE_FIXTURE,),
    name='CollectiveDocumentfileLayer:IntegrationTesting'
)


COLLECTIVE_DOCUMENTFILE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_DOCUMENTFILE_FIXTURE,),
    name='CollectiveDocumentfileLayer:FunctionalTesting'
)


COLLECTIVE_DOCUMENTFILE_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_DOCUMENTFILE_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveDocumentfileLayer:AcceptanceTesting'
)
