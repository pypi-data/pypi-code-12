# -*- coding: utf-8 -*-
"""Migration steps for ps.plone.mls."""

# zope imports
from plone import api

# local imports
from ps.plone.mls import config


def migrate_to_1001(context):
    """Migrate from 1000 to 1001.

    * Activate portal actions.
    """
    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(config.INSTALL_PROFILE, 'actions')


def migrate_to_1002(context):
    """Migrate from 1001 to 1002.

    * ensure mls.css
    """
    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(config.INSTALL_PROFILE, 'cssregistry')
    setup.runImportStepFromProfile(config.INSTALL_PROFILE, 'jsregistry')


def migrate_css(context):
    """Migration step for simple css updates."""
    setup = api.portal.get_tool(name='portal_setup')
    setup.runImportStepFromProfile(config.INSTALL_PROFILE, 'cssregistry')


def migrate_to_1005(context):
    """Migrate from 1004 to 1005

    * add ps.plone.realestatefont
    """
    quickinstaller = api.portal.get_tool(name='portal_quickinstaller')

    # Add ps.fonts.iconmagic
    if not quickinstaller.isProductInstalled('ps.plone.realestatefont'):
        quickinstaller.installProduct('ps.plone.realestatefont')
