from ftw.testing.layer import COMPONENT_REGISTRY_ISOLATION
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from zope.configuration import xmlconfig


class ProfilehookLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        import ftw.profilehook
        xmlconfig.file('configure.zcml',
                       ftw.profilehook,
                       context=configurationContext)


PROFILEHOOK_FIXTURE = ProfilehookLayer()
PROFILEHOOK_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PROFILEHOOK_FIXTURE,
           COMPONENT_REGISTRY_ISOLATION),
    name="integration")
