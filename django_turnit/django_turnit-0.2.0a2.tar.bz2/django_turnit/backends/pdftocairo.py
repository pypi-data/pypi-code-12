# -*- coding: utf-8 -*-
"""
Thumbnailer to create or update thumbnails with help to `pdftocairo` for PDF files, using subprocess

..see:: `pdftocairo <http://manpages.ubuntu.com/manpages/precise/man1/pdftocairo.1.html>`_

:creationdate: 14/03/16 13:03
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.backends.pdf2cairo

"""
import os
import re
import logging
import shlex
import subprocess
from collections import OrderedDict
from copy import copy

from django.conf import settings

from django_turnit.backends import PDFThumbnailerBase, PDFThumbnailerError
from django_turnit.backends.base import get_page_filepath
from django_turnit.utilities import cmd_exists

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.backends.pdf2cairo')


class PDFThumbnailer(PDFThumbnailerBase):
    """
    Create thumbnail images using *subprocessed* pdftocairo command
    """
    command = copy(settings.TURNIT_PDFTOCAIRO_CMD)
    _initial_args = copy(settings.TURNIT_PDFTOCAIRO_GLOBAL_ARGS)
    _initial_args.insert(0, '-%s' % settings.TURNIT_IMAGE_EXT)
    lib_args = None
    file_ext = settings.TURNIT_IMAGE_EXT

    def __init__(self, pdf_file, item_id, **kwargs):
        super(PDFThumbnailer, self).__init__(pdf_file, item_id, **kwargs)
        if not cmd_exists(self.command):
            raise EnvironmentError('The executable %s does not exists on this system. You have to install it !' %
                                   self.command)

    def get_image_filepath(self, page_filepath):
        if page_filepath.endswith(self.file_ext):
            new_page_filepath = '.'.join(page_filepath.split('.')[:-1])
            settings.DEBUG and logger.debug(u'PDFThumbnailer::get_image_filepath() '
                                            u'page_filepath %s needs ext truncating : \n%s',
                                            page_filepath, new_page_filepath)

            return new_page_filepath

    def get_thumbnail_for_page(self, page_id):
        args, extra_params = self.get_lib_args(page_id=page_id)
        page_filepath = get_page_filepath(pdf_file=self.pdf_file,
                                          page_id=page_id,
                                          prefix=self.prefix,
                                          guid=self.guid,
                                          **extra_params)
        # Adds the input file name
        args.append('-')
        # Appends the file output
        args.append(self.get_image_filepath(page_filepath=page_filepath))

        command = [self.command]
        command.extend(args)
        command = ' '.join(command)  # Joins the command before re-parsing it
        command = shlex.split(command)
        self.last_args = command
        settings.DEBUG and logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() command = \n%s', command)
        # process thumbnails
        data, error = None, None
        with open(self.full_path, 'rb') as pdf_file:
            try:
                process = subprocess.Popen(command,
                                           stdin=pdf_file,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                data, error = process.communicate()
                if data.strip():
                    settings.DEBUG and logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() data = \n*%s*', data)
                if error.strip():
                    settings.DEBUG and logger.debug(u'PDFThumbnailer::get_thumbnail_for_page() error = \n*%s*', error)
            except subprocess.CalledProcessError as e:
                logger.error(
                    u'PDFThumbnailer::get_thumbnail_for_page() '
                    u'Unable to generate thumbnail for PDF \ndata: %s \nerror: %s',
                    data, error)
                raise PDFThumbnailerError(e)
        return page_filepath, self.last_args

    def get_lib_args(self, page_id=None):
        """
        Gets the args for using the pdftocairo command inside a subprocess
        :param page_id:
        :return:
        """
        extra_params = OrderedDict()
        self.lib_args = []
        self.lib_args.extend(self._initial_args)
        # Update cropbox / singnefile
        if '-cropbox' in self.lib_args:
            extra_params.update({'cropbox': 1})
        if '-singlefile' in self.lib_args:
            extra_params.update({'singlefile': 1})
        # Gets size extra parameters (self.lib_args is updated)
        extra_params.update(self.get_size_args())

        # Sets the current page to transform
        if page_id:
            self.lib_args.append('-f %s' % page_id)
            self.lib_args.append('-l %s' % page_id)
        return self.lib_args, extra_params

    def get_size_args(self):
        extra_params = OrderedDict()
        if hasattr(self, 'width') and hasattr(self, 'height'):
            if self.width:
                width = getattr(self, 'width')
                self.lib_args.append('-scale-to-x %d' % width)
                extra_params['w'] = width
            if self.height:
                height = getattr(self, 'height')
                self.lib_args.append('-scale-to-y %d' % height)
                extra_params['h'] = height
        elif hasattr(self, 'resolution_x') and hasattr(self, 'resolution_y'):
            if self.resolution_x == self.resolution_y:
                self.lib_args.append('-r %d' % self.resolution_x)
                extra_params['r'] = str(self.resolution_x)
            else:
                self.lib_args.append('-rx %d' % self.resolution_x)
                self.lib_args.append('-ry %d' % self.resolution_y)
                extra_params['rx'] = self.resolution_x
                extra_params['ry'] = self.resolution_y
        else:
            # noinspection PyStringFormat
            rx, ry = getattr(self, 'resolution', None) or settings.TURNIT_OUTPUT_IMAGE_RESOLUTION
            resolution_x = '-rx %s' % rx
            resolution_y = '-ry %s' % ry
            self.lib_args.append(resolution_x)
            self.lib_args.append(resolution_y)
            extra_params['rx'] = rx
            extra_params['ry'] = ry
        return extra_params
