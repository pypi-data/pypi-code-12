# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import collective.pdfdocument


class CollectivePdfdocumentLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.pdfdocument)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.pdfdocument:default')


COLLECTIVE_PDFDOCUMENT_FIXTURE = CollectivePdfdocumentLayer()


COLLECTIVE_PDFDOCUMENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PDFDOCUMENT_FIXTURE,),
    name='CollectivePdfdocumentLayer:IntegrationTesting'
)


COLLECTIVE_PDFDOCUMENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PDFDOCUMENT_FIXTURE,),
    name='CollectivePdfdocumentLayer:FunctionalTesting'
)


COLLECTIVE_PDFDOCUMENT_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_PDFDOCUMENT_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectivePdfdocumentLayer:AcceptanceTesting'
)
