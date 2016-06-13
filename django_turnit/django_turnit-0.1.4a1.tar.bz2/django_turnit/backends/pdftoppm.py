# -*- coding: utf-8 -*-
"""
Thumbnailer to create or update thumbnails with help to `pdftoppm` for PDF files, using subprocess

..see:: `pdftoppm <http://manpages.ubuntu.com/manpages/precise/man1/pdftoppm.1.html>`_

:creationdate: 15/03/16 08:38
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.backends.pdftoppm

"""
import logging
from copy import copy

from django.conf import settings

from django_turnit.backends.pdftocairo import PDFThumbnailer as p2c_PDFThumbnailer

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.backends.pdftoppm')


class PDFThumbnailer(p2c_PDFThumbnailer):
    """
    Create thumbnail images using *subprocessed* pdftoppm command
    """
    command = copy(settings.TURNIT_PDFTOPPM_CMD)
    _initial_args = copy(settings.TURNIT_PDFTOPPM_GLOBAL_ARGS)
    _initial_args.insert(0, '-%s' % settings.TURNIT_PDFTOPPM_IMAGE_FORMAT)
    lib_args = None
