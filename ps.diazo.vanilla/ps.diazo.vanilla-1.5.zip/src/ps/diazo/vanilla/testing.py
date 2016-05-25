# -*- coding: utf-8 -*-
"""Test Layer for ps.diazo.vanilla."""

# zope imports
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
    applyProfile,
)
from plone.testing import (
    Layer,
    z2,
)


class PsDiazoVanillaLayer(PloneSandboxLayer):
    """Custom Test Layer for ps.diazo.vanilla."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        """Set up Zope for testing."""
        # Load ZCML
        import ps.diazo.vanilla
        self.loadZCML(package=ps.diazo.vanilla)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'ps.diazo.vanilla:default')


PS_DIAZO_VANILLA_FIXTURE = PsDiazoVanillaLayer()


PS_DIAZO_VANILLA_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PS_DIAZO_VANILLA_FIXTURE,),
    name='PsDiazoVanillaLayer:IntegrationTesting'
)


PS_DIAZO_VANILLA_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PS_DIAZO_VANILLA_FIXTURE,),
    name='PsDiazoVanillaLayer:FunctionalTesting'
)


PS_DIAZO_VANILLA_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PS_DIAZO_VANILLA_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='PsDiazoVanillaLayer:AcceptanceTesting'
)


ROBOT_TESTING = Layer(name='ps.diazo.vanilla:Robot')
