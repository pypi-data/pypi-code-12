# -*- coding: utf-8 -*-

from brasil.gov.portlets.config import PROJECTNAME
from brasil.gov.portlets.interfaces import IBrowserLayer
from brasil.gov.portlets.testing import FUNCTIONAL_TESTING
from brasil.gov.portlets.testing import INTEGRATION_TESTING
from plone.browserlayer.utils import registered_layers
from plone.portlets.interfaces import IPortletManager
from Products.GenericSetup.upgrade import listUpgradeSteps
from zope.component import getUtility

import unittest


class Plone43TestCase(unittest.TestCase):

    layer = FUNCTIONAL_TESTING


class BaseTestCase(unittest.TestCase):
    """Base test case to be used by other tests."""

    layer = INTEGRATION_TESTING

    profile = 'brasil.gov.portlets:default'

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = self.portal['portal_quickinstaller']
        self.wt = self.portal['portal_workflow']
        self.st = self.portal['portal_setup']


class TestInstall(BaseTestCase):
    """Ensure product is properly installed."""

    def test_installed(self):
        self.assertTrue(
            self.qi.isProductInstalled(PROJECTNAME),
            '{0} not installed'.format(PROJECTNAME)
        )

    def test_browser_layer_installed(self):
        self.assertIn(IBrowserLayer, registered_layers())

    def test_version(self):
        self.assertEqual(
            self.st.getLastVersionForProfile(self.profile),
            (u'1001',)
        )


class TestUpgrade(BaseTestCase):
    """Ensure product upgrades work."""

    def list_upgrades(self, source, destination):
        upgradeSteps = listUpgradeSteps(self.st, self.profile, source)
        if source == '0':
            source = (source, '0')
        else:
            source = (source, )

        step = [
            step for step in upgradeSteps
            if (step[0]['dest'] == (destination,))
            and (step[0]['source'] == source)
        ]
        return step

    def execute_upgrade(self, source, destination):
        # Setamos o profile para versao source
        self.st.setLastVersionForProfile(self.profile, source)

        # Pegamos os upgrade steps
        upgradeSteps = listUpgradeSteps(self.st, self.profile, source)
        if source == '0':
            source = (source, '0')
        else:
            source = (source, )
        steps = [
            step for step in upgradeSteps
            if (step[0]['dest'] == (destination,))
            and (step[0]['source'] == source)
        ][0]
        # Os executamos
        for step in steps:
            step['step'].doStep(self.st)

    def test_to1000_available(self):
        step = self.list_upgrades(u'unknown', u'1000')
        self.assertEqual(len(step), 1)

    def test_to1001_available(self):
        step = self.list_upgrades(u'1000', u'1001')
        self.assertEqual(len(step), 1)

    def test_to1001_execution(self):
        self.execute_upgrade(u'1000', u'1001')

        for column in ['plone.leftcolumn', 'plone.rightcolumn']:
            manager = getUtility(IPortletManager, name=column)
            addable_portlet_types = [
                a.title for a in manager.getAddablePortletTypes()
            ]

        new_strings = [
            u'Portal Padrao Collection',
            u'Portal Padrao Audio Gallery',
            u'Portal Padrao Audio',
            u'Portal Padrao Video',
            u'Portal Padrao Video Gallery',
            u'Portal Padrao Media Carousel'
        ]

        self.assertTrue(
            all([string in addable_portlet_types for string in new_strings])
        )

    def test_ultimo_upgrade_igual_metadata_xml_filesystem(self):
        """
        Testa se o número do último upgradeStep disponível é o mesmo do
        metadata.xml do profile.
        É também útil para garantir que para toda alteração feita no version
        do metadata.xml tenha um upgradeStep associado.
        Esse teste parte da premissa que o número dos upgradeSteps é sempre
        sequencial.
        """
        upgrade_info = self.qi.upgradeInfo(PROJECTNAME)
        upgradeSteps = listUpgradeSteps(self.st, self.profile, '')
        upgrades = [upgrade[0]['dest'][0] for upgrade in upgradeSteps]
        last_upgrade = sorted(upgrades, key=int)[-1]
        self.assertEqual(upgrade_info['installedVersion'], last_upgrade)


class TestUninstall(BaseTestCase):
    """Ensure product is properly uninstalled."""

    def setUp(self):
        BaseTestCase.setUp(self)
        self.qi.uninstallProducts(products=[PROJECTNAME])

    def test_uninstalled(self):
        self.assertFalse(self.qi.isProductInstalled(PROJECTNAME))

    def test_browser_layer_removed_uninstalled(self):
        self.assertNotIn(IBrowserLayer, registered_layers())
