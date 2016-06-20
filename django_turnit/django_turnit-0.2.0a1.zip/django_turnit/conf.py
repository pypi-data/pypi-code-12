# -*- coding: utf-8 -*-
"""
Application settings for :mod:`django_turnit` application

:creationdate: 07/03/16 13:23
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.conf

"""
import logging
from collections import namedtuple

from appconf import AppConf

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.conf')


class DjangoTurnitAppConf(AppConf):
    """
    django_turnit default applications settings
    """
    #: MIME type of files supported by django_turnit
    INPUT_SUPPORTED_FILE_TYPES = ['application/pdf', ]

    #: Folder where turnit thumbnails are saved
    OUTPUT_MEDIA_ROOT = 'django_turnit'

    OUTPUT_FILE_FMT = '%(basename)s-%(guid)s-p%%04d-%(param)s.%(ext)s'
    """
    Output file mane format. Supports `basename`, 'guid', 'param' and `ext` substitutions.

    .. note:: The numbering is automatically performed
    """

    #: Output image resolution, as a pair (resolution_x, resolution_y)
    OUTPUT_IMAGE_RESOLUTION = (150, 150)

    #: Output image format (default PNG)
    IMAGE_EXT = 'png'

    THUMBNAILER_BACKEND = 'django_turnit.backends.gs.PDFThumbnailer'
    """
    Sets the default backend for thumbnailing, as a class
    Choices are:

    - 'django_turnit.backends.gs.PDFThumbnailer':
        `Ghostscript <http://ghostscript.com/>`_ library through `python-ghostscript  <https://pypi.python.org/pypi/ghostscript>`_
    - 'django_turnit.backends.pdftocairo.PDFThumbnailer':
        `pdftocairo <http://manpages.ubuntu.com/manpages/precise/man1/pdftocairo.1.html>`_ through subprocess
    - 'django_turnit.backends.pdftoppm.PDFThumbnailer':
        `pdftoppm <http://manpages.ubuntu.com/manpages/precise/man1/pdftoppm.1.html>`_ through subprocess
    """

    # Ghostscript settings

    #: Ghostscript global settings for <http://www.ghostscript.com/>`_ library
    GHOSTSCRIPT_GLOBAL_ARGS = ['-q',
                               '-dQUIET',
                               '-dNOPAUSE',
                               '-dBATCH',
                               '-dSAFER',
                               ]

    #: Output image format (default: 'png16m')
    GHOSTSCRIPT_IMAGE_FORMAT = 'png16m'

    #: Ghostscript extra settings
    GHOSTSCRIPT_EXTRA_ARGS = []

    # pdftocairo settings

    #: `pdftocairo` command format
    PDFTOCAIRO_CMD = '/usr/bin/pdftocairo'

    #: `pdftocairo` global settings
    PDFTOCAIRO_GLOBAL_ARGS = ['-cropbox', '-singlefile', ]

    # `pdftoppm` settings

    #: `pdftoppm` command
    PDFTOPPM_CMD = '/usr/bin/pdftoppm'

    #: `pdftoppm` global settings
    PDFTOPPM_GLOBAL_ARGS = ['-cropbox', '-singlefile', ]

    class Meta:
        prefix = 'turnit'
