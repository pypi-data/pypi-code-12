# -*- coding: utf-8 -*-
"""Propertyshelf MLS Plone Embedding."""

# python imports
import logging

# zope imports
from zope.i18nmessageid import MessageFactory

# local imports
from ps.plone.mls import config

logger = logging.getLogger(config.PROJECT_NAME)
_ = MessageFactory('ps.plone.mls')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
