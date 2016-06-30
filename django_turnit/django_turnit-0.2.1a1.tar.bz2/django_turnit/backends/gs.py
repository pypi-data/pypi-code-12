# -*- coding: utf-8 -*-
"""
Thumbnailer to create or update thumbnails for PDF files, using `ghostscript <http://ghostscript.com/>`_

:creationdate: 09/03/16 10:02
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.thumbnailer

"""
from django_turnit.backends import PDFThumbnailerBase
from django_turnit.backends.base import get_page_filepath

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import logging
import os
import timeit
import uuid
from copy import copy

try:
    import ghostscript
    from ghostscript import GhostscriptError
except ImportError as e:
    raise ImportError('You MUST install the python-ghostscript binding to use Ghostscript as thumbnailer library', e)

from django.conf import settings
from pdfminer import pdfpage

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.backends.gs')


class PDFThumbnailer(PDFThumbnailerBase):
    """
    Generate thumbnails for PDF file
    """
    stdin = None
    stdout = None

    def initialize_backend(self):
        """
        Extra initialization for the backend
        """
        # Creates initial settings for ghostscript
        self._gs_initial_args = copy(settings.TURNIT_GHOSTSCRIPT_GLOBAL_ARGS)
        # Update file output format
        self._gs_initial_args.append('-sDEVICE=%s' % settings.TURNIT_GHOSTSCRIPT_IMAGE_FORMAT)

    def get_thumbnail_for_page(self, page_id):
        """
        Gets the thumbnail image for a given page ID

        :param page_id: page identidier (int)
        :returns: page image file name
        :raises: GhostscriptError on a ghostscript error
        """
        settings.DEBUG and logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() self.full_path = %s', self.full_path)
        # Gets the natural args
        args, extra_kwargs = self.get_lib_args(page_id)
        page_filepath = get_page_filepath(pdf_file=self.pdf_file,
                                          page_id=page_id,
                                          prefix=self.prefix,
                                          guid=self.guid,
                                          **extra_kwargs)

        # Appends the file output
        args.append('-o')
        args.append(page_filepath)
        args.append(self.full_path)
        settings.DEBUG and logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() args = %s', args)
        self.last_args = ['GS']
        self.last_args.extend(args)
        stdout, stderr = StringIO(), StringIO()
        try:
            tic, toc = 0, 0
            if settings.DEBUG:
                tic = timeit.default_timer()
            # Launch Ghostscript
            gs = ghostscript.Ghostscript(*args, stdout=stdout, stderr=stderr)

            if settings.DEBUG:
                toc = timeit.default_timer()
                logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() '
                             u'\nself.gs = %s'
                             u'\nstdout.getvalue() = %s'
                             u'\nstderr.getvalue() = %s'
                             U'\n timer = %d',
                             gs,
                             stdout.getvalue(),
                             stderr.getvalue(),
                             toc - tic)
        except GhostscriptError as e:
            logger.error('PDFThumbnailer::get_thumbnail_for_page() unable to generate thumbnail for pdf %s : %s',
                         self.pdf_file, e)
            settings.DEBUG and logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() '
                                            u'stdout.getvalue() = %s / '
                                            u'stderr.getvalue() = %s',
                                            stdout.getvalue(),
                                            stderr.getvalue())
            raise
        finally:
            ghostscript.cleanup()
            if not stderr.closed:
                stderr.close()
            if not stdout.closed:
                stdout.close()
        return page_filepath, self.last_args

    def gs_get_size_args(self):
        extra_params = {}
        if hasattr(self, 'width') and hasattr(self, 'height'):
            if self.width:
                width = getattr(self, 'width')
                self.lib_args.append('-dDEVICEWIDTH=%d' % width)
                extra_params['w'] = width
            if self.height:
                height = getattr(self, 'height')
                self.lib_args.append('-dDEVICEHEIGHT=%d' % height)
                extra_params['h'] = height
        elif hasattr(self, 'resolution_x') and hasattr(self, 'resolution_y'):
            resolution = '%dx%d' % (getattr(self, 'resolution_x'), getattr(self, 'resolution_y'))
            self.lib_args.append('-r%s' % resolution)
            extra_params['r'] = resolution
        else:
            # noinspection PyStringFormat
            resolution = '%sx%s' % (getattr(self, 'resolution', None) or settings.TURNIT_OUTPUT_IMAGE_RESOLUTION)
            self.lib_args.append('-r%s' % resolution)
            extra_params['r'] = resolution
        return extra_params

    def get_lib_args(self, page_id=None):
        """
        Creates the Ghostscripts args

        :param page_id: page index
        :returns: List of arguments
        """
        extra_params = {}
        self.lib_args = []
        self.lib_args.extend(self._gs_initial_args)
        extra_params.update(self.gs_get_size_args())

        # Sets the current page to transform
        if page_id:
            self.lib_args.append('-dFirstPage=%s' % page_id)
            self.lib_args.append('-dLastPage=%s' % page_id)

        # Appends additional args from `settings.TURNIT_GHOSTSCRIPT_EXTRA_ARGS`
        if settings.TURNIT_GHOSTSCRIPT_EXTRA_ARGS:
            for arg in settings.TURNIT_GHOSTSCRIPT_EXTRA_ARGS:
                if arg not in self.lib_args:
                    self.lib_args.append(arg)
        settings.DEBUG and logger.debug(u'PDFThumbnailer::get_lib_args() self.lib_args = %s', self.lib_args)
        return self.lib_args, extra_params


