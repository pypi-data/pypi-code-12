# -*- coding: utf-8 -*-
"""Zope2 install and uninstall."""

# local imports
from ps.plone.mls import (
    config,
    logger,
)


def uninstall(portal, reinstall=False):
    """Uninstall the add-on."""
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile(config.UNINSTALL_PROFILE)
        logger.info('Uninstall done')
