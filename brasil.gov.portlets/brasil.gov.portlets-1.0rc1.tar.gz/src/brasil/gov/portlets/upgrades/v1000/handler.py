# -*- coding: utf-8 -*-
from brasil.gov.portlets.config import PROJECTNAME
from brasil.gov.portlets.setuphandlers import register_vendor_js
from plone.app.upgrade.utils import loadMigrationProfile

import logging


def apply_profile(context):
    """Atualiza perfil para versao 1000."""
    logger = logging.getLogger(PROJECTNAME)
    profile = 'profile-brasil.gov.portlets.upgrades.v1000:default'
    loadMigrationProfile(context, profile)
    register_vendor_js(context)
    logger.info('Atualizado para versao 1000')
