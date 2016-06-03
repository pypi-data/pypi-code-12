# -*- coding: utf-8 -*-
"""Init and utils."""

import logging
from zope.i18nmessageid import MessageFactory


PKG_NAME = "collective.filemeta"

ANNOTATION_KEY = "filemeta"

_ = MessageFactory(PKG_NAME)

logger = logging.getLogger(PKG_NAME)
