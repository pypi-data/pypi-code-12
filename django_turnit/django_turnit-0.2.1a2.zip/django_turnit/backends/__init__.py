# -*- coding: utf-8 -*-
"""
Base classes and settings for thumbnailers
"""
import logging
from importlib import import_module
from django.conf import settings

from django_turnit.backends.base import PDFThumbnailerError, PDFThumbnailerBase

logger = logging.getLogger('django_turnit.backends')


def get_backend_class():
    """
    Loads the backend used to create the thumbnail image from the PDF file

    :returns: backend **class**
    """
    backend_name = settings.TURNIT_THUMBNAILER_BACKEND
    settings.DEBUG and logger.debug(u'get_backend_class() required backend : %s', backend_name)
    module_name = '.'.join(backend_name.split('.')[:-1])
    class_name = backend_name.split('.')[-1]
    settings.DEBUG and logger.debug(u'get_backend_class() module_name = %s / class_name = %s', module_name, class_name)

    try:
        mod = import_module(module_name)
    except ImportError as e:
        logger.error(u'get_backend_class() Unable to get the backend for %s', backend_name)
        raise PDFThumbnailerError(e)
    if hasattr(mod, class_name):
        klass = getattr(mod, class_name)
        settings.DEBUG and logger.debug(u'get_backend_class() selected backend: %s', backend_name)
        if not issubclass(klass, PDFThumbnailerBase):
            raise PDFThumbnailerError('*%s* is not a subclass of PDFThumbnailerBase.' % backend_name)
        return klass
