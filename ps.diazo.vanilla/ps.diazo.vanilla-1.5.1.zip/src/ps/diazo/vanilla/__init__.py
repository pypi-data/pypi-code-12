# -*- coding: utf-8 -*-
"""Propertyshelf Vanilla Theme."""

# python imports
import logging

# zope imports
from zope.i18nmessageid import MessageFactory

# local imports
from ps.diazo.vanilla import config

logger = logging.getLogger(config.PROJECT_NAME)
_ = MessageFactory('ps.diazo.vanilla')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
