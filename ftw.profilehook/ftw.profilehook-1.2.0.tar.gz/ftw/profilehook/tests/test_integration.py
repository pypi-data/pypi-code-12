from ftw.profilehook.testing import PROFILEHOOK_INTEGRATION_TESTING
from plone.app.testing import applyProfile
from Products.CMFCore.utils import getToolByName
from unittest2 import TestCase


execution_log = []


def hook(site):
    execution_log.append('hook')


def before_import_hook(site):
    execution_log.append('before import hook')


def import_step(site):
    execution_log.append('import step')


class TestIntegration(TestCase):
    layer = PROFILEHOOK_INTEGRATION_TESTING

    def tearDown(self):
        super(TestIntegration, self).tearDown()
        execution_log[:] = []

    def test_hook_is_called_after_profile_is_imported(self):
        self.layer['load_zcml_string'](
            '<configure'
            '    package="ftw.profilehook.tests"'
            '    xmlns="http://namespaces.zope.org/zope"'
            '    xmlns:genericsetup="http://namespaces.zope.org/genericsetup"'
            '    xmlns:i18n="http://namespaces.zope.org/i18n"'
            '    xmlns:profilehook="http://namespaces.zope.org/profilehook"'
            '    i18n_domain="ftw.profilehook">'

            '  <genericsetup:registerProfile'
            '      name="foo"'
            '      title="ftw.profilehook.tests"'
            '      directory="profiles/foo"'
            '      provides="Products.GenericSetup.interfaces.EXTENSION"'
            '      />'

            '  <genericsetup:importStep'
            '      name="ftw.profilehook.tests"'
            '      title="ftw.profilehook.test"'
            '      description=""'
            '      handler="{0}.import_step"'
            '      />'

            '  <include package="ftw.profilehook" />'
            '  <profilehook:hook'
            '      profile="ftw.profilehook.tests:foo"'
            '      handler="{0}.hook"'
            '      />'
            '</configure>'.format(self.__module__))

        applyProfile(
            self.layer['portal'], 'ftw.profilehook.tests:foo')

        self.assertEquals(['import step', 'hook'], execution_log)

    def test_hook_is_not_called_when_other_profiles_are_imported(self):
        self.layer['load_zcml_string'](
            '<configure'
            '    package="ftw.profilehook.tests"'
            '    xmlns="http://namespaces.zope.org/zope"'
            '    xmlns:genericsetup="http://namespaces.zope.org/genericsetup"'
            '    xmlns:i18n="http://namespaces.zope.org/i18n"'
            '    xmlns:profilehook="http://namespaces.zope.org/profilehook"'
            '    i18n_domain="ftw.profilehook">'

            '  <genericsetup:registerProfile'
            '      name="foo"'
            '      title="ftw.profilehook.tests"'
            '      directory="profiles/foo"'
            '      provides="Products.GenericSetup.interfaces.EXTENSION"'
            '      />'

            '  <include package="ftw.profilehook" />'
            '  <profilehook:hook'
            '      profile="ftw.profilehook.tests:bar"'
            '      handler="{0}.hook"'
            '      />'
            '</configure>'.format(self.__module__))

        applyProfile(
            self.layer['portal'], 'ftw.profilehook.tests:foo')

        self.assertEquals([], execution_log)

    def test_hook_is_not_called_when_not_all_import_steps_are_executed(self):
        self.layer['load_zcml_string'](
            '<configure'
            '    package="ftw.profilehook.tests"'
            '    xmlns="http://namespaces.zope.org/zope"'
            '    xmlns:genericsetup="http://namespaces.zope.org/genericsetup"'
            '    xmlns:i18n="http://namespaces.zope.org/i18n"'
            '    xmlns:profilehook="http://namespaces.zope.org/profilehook"'
            '    i18n_domain="ftw.profilehook">'

            '  <genericsetup:registerProfile'
            '      name="foo"'
            '      title="ftw.profilehook.tests"'
            '      directory="profiles/foo"'
            '      provides="Products.GenericSetup.interfaces.EXTENSION"'
            '      />'

            '  <include package="ftw.profilehook" />'
            '  <profilehook:hook'
            '      profile="ftw.profilehook.tests:foo"'
            '      handler="{0}.hook"'
            '      />'
            '</configure>'.format(self.__module__))

        profile_id = 'profile-ftw.profilehook.tests:foo'
        setup_tool = getToolByName(self.layer['portal'], 'portal_setup')

        setup_tool.runImportStepFromProfile(profile_id, 'actions')
        self.assertEquals([], execution_log)

        setup_tool.runAllImportStepsFromProfile(profile_id)
        self.assertEquals(['hook'], execution_log)

    def test_before_import_hook_is_executed_before_profile_is_imported(self):
        self.layer['load_zcml_string'](
            '<configure'
            '    package="ftw.profilehook.tests"'
            '    xmlns="http://namespaces.zope.org/zope"'
            '    xmlns:genericsetup="http://namespaces.zope.org/genericsetup"'
            '    xmlns:i18n="http://namespaces.zope.org/i18n"'
            '    xmlns:profilehook="http://namespaces.zope.org/profilehook"'
            '    i18n_domain="ftw.profilehook">'

            '  <genericsetup:registerProfile'
            '      name="foo"'
            '      title="ftw.profilehook.tests"'
            '      directory="profiles/foo"'
            '      provides="Products.GenericSetup.interfaces.EXTENSION"'
            '      />'

            '  <genericsetup:importStep'
            '      name="ftw.profilehook.tests"'
            '      title="ftw.profilehook.test"'
            '      description=""'
            '      handler="{0}.import_step"'
            '      />'

            '  <include package="ftw.profilehook" />'
            '  <profilehook:hook'
            '      profile="ftw.profilehook.tests:foo"'
            '      handler="{0}.hook"'
            '      />'

            '  <profilehook:before_import_hook'
            '      profile="ftw.profilehook.tests:foo"'
            '      handler="{0}.before_import_hook"'
            '      />'

            '</configure>'.format(self.__module__))

        applyProfile(
            self.layer['portal'], 'ftw.profilehook.tests:foo')

        self.assertEquals(['before import hook',
                           'import step',
                           'hook'], execution_log)
