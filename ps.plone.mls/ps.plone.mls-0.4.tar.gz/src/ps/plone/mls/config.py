# -*- coding: utf-8 -*-
"""Configuration options for the Propertyshelf MLS Plone Embedding."""

PROFILE_ID = u'profile-ps.plone.mls'
INSTALL_PROFILE = '{0}:default'.format(PROFILE_ID)
UNINSTALL_PROFILE = '{0}:uninstall'.format(PROFILE_ID)
PROJECT_NAME = 'ps.plone.mls'

#: Configuration key for development collection settings.
SETTINGS_DEVELOPMENT_COLLECTION = 'ps.plone.mls.developmentcollection'
