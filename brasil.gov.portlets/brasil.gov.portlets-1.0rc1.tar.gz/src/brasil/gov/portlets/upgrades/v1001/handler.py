# -*- coding: utf-8 -*-

from brasil.gov.portlets.config import PROJECTNAME
from plone.app.upgrade.utils import loadMigrationProfile

import logging


def apply_profile(context):
    """Atualiza perfil para versao 1001."""
    logger = logging.getLogger(PROJECTNAME)
    profile = 'profile-brasil.gov.portlets.upgrades.v1001:default'
    loadMigrationProfile(context, profile)
    logger.info('Atualizado para versao 1001')
