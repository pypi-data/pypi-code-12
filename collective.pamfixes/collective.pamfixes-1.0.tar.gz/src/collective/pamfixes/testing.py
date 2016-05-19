# -*- coding: utf-8 -*-
"""Test setup for collective.pamfixes"""

# zope imports
from OFS.Folder import Folder
from Testing import ZopeTestCase as ztc
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PLONE_FIXTURE,
    PloneSandboxLayer,
    setRoles,
    TEST_USER_ID,
)
import transaction

# local imports
import collective.pamfixes


class CollectivePamfixesLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    class Session(dict):
        def set(self, key, value):
            self[key] = value

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=collective.pamfixes)
        self.loadZCML(name='testing.zcml', package=collective.pamfixes)
        self.loadZCML(name='overrides.zcml', package=collective.pamfixes)

        # Support sessionstorage in tests
        app.REQUEST['SESSION'] = self.Session()
        if not getattr(app, 'temp_folder', None):
            tf = Folder('temp_folder')
            app._setObject('temp_folder', tf)
            transaction.commit()

        ztc.utils.setupCoreSessions(app)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.pamfixes:testfixture')

        # Empower test user
        setRoles(portal, TEST_USER_ID, ['Manager'])


COLLECTIVE_PAMFIXES_FIXTURE = CollectivePamfixesLayer()


COLLECTIVE_PAMFIXES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_PAMFIXES_FIXTURE,),
    name='CollectivePamfixesLayer:IntegrationTesting'
)


COLLECTIVE_PAMFIXES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_PAMFIXES_FIXTURE,),
    name='CollectivePamfixesLayer:FunctionalTesting'
)
