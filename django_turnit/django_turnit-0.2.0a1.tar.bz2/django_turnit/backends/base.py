# -*- coding: utf-8 -*-
"""
Base function and API for thumbnailing backends

:creationdate: 14/03/16 13:21
:moduleauthor: François GUÉRIN <fguerin@ville-tourcoing.fr>
:modulename: django_turnit.backends.base

"""
import logging
import os
import timeit
import uuid

from django.conf import settings
from django.db import transaction
from pdfminer import pdfpage

from django_turnit import models
from django_turnit.utilities import get_file_hash

__author__ = 'fguerin'
logger = logging.getLogger('django_turnit.backends.base')


class PDFThumbnailerBase(object):
    """
    Generic abstract implementation for a PDF thumbnailer.
    This base class includes
    """
    last_args = None

    def __init__(self, pdf_file, item_id, dry_run=False, **kwargs):
        super(PDFThumbnailerBase, self)
        self.pdf_file = pdf_file
        self.item_id = item_id
        self.dry_run = dry_run
        self.full_path = os.path.join(settings.MEDIA_ROOT, pdf_file.name)
        self.prefix = os.path.join(settings.MEDIA_ROOT, settings.TURNIT_OUTPUT_MEDIA_ROOT)
        # Check for keywords arguments
        for k, v in kwargs.items():
            setattr(self, k, v)
        # Initialize extra data for backend
        self.initialize_backend()
        # Count pages
        self.guid = str(uuid.uuid4())[:8]  # Generate a guid
        self.page_count = self.get_page_count()
        self.page_image_list = []
        self.pdffilepage_list, self.hash, self.need_update = None, None, None


    def initialize_backend(self):
        """
        Adds extra initialization for backend
        """
        pass

    def get_page_count(self):
        """
        Gets the page count from a PDF file

        :param pdf_file: PDF file field instance
        :returns: page count
        :raises: GhostscriptError on a ghostscript error
        """
        try:
            with open(self.full_path, 'rb') as pdf_file:
                pages = list(pdfpage.PDFPage.get_pages(pdf_file))
                page_count = len(pages)
                settings.DEBUG and logger.debug(u'PDFThumbnailerBase::get_page_count() page_count = %s', page_count)
        except IOError:
            logger.error(u'PDFThumbnailerBase::get_page_count() Unable to find file %s', self.full_path)
            raise
        return page_count

    @transaction.atomic
    def get_thumbnails(self):
        """
        Gets the list of thumbnails

        :returns: list of thumbnails
        """
        if self.page_count is None:
            logger.error(u'PDFThumbnailerBase::get_thumbnails() No page count for this document.')
        # Timing
        tic, toc = 0, 0
        if settings.DEBUG:
            tic = timeit.default_timer()

        self.pdffilepage_list, self.hash, self.need_update = self.get_database_pdffile_list()

        if not self.need_update:
            return [pdffilepage.page_file.name for pdffilepage in self.pdffilepage_list]

        for pdffilepage in self.pdffilepage_list:
            thumbnail_image, last_args = self.get_thumbnail_for_page(pdffilepage.page_id)
            self.page_image_list.append(thumbnail_image)
            settings.DEBUG and logger.debug(u'PDFThumbnailerBase::get_thumbnails() self.page_image_list = %s',
                                            self.page_image_list)
            self.update_database(pdffilepage=pdffilepage, page_id=pdffilepage.page_id, thumbnail_image=thumbnail_image)

        if settings.DEBUG:
            toc = timeit.default_timer()
            logger.debug(u'PDFThumbnailerBase::get_thumbnails() timeit : %s seconds', toc - tic)
        return self.page_image_list

    def get_thumbnail_for_page(self, page_id):
        """
        Gets the thumbnail image for a given page ID

        :param page_id: page identidier (int)
        :returns: <page image file name>, <last_args>
        """
        raise NotImplementedError

    # Creates / updates the PDFFilePage in database
    def get_database_pdffile_list(self):
        """
        Gets or creates the :class:`django_turnit.models.PDFFilePage` from database by md5 hash, and store in into
         a list

        :returns: <list of pages>, <need thumbnail>
        """
        file_hash = get_file_hash(self.full_path)
        settings.DEBUG and logger.debug(u'PDFThumbnailerBase::get_database_pdffile_list() file_hash = %s',
                                        file_hash)
        pdffilepage_list = models.PDFFilePage.objects.filter(related_pdf_file=self.pdf_file.name,
                                                             pdffile_hash=file_hash)
        if pdffilepage_list:
            logger.info(u'PDFThumbnailerBase::get_database_pdffile_list() PDFFilePage already exists, with hash, '
                        u'no need to update thumbnails.')
            return list(pdffilepage_list), file_hash, False

        # PDFFilePage does not exists in database, will create them
        pdffilepage_list = []
        need_updating = True
        for page_id in range(1, self.page_count + 1):
            pdffilepage, created = models.PDFFilePage.objects.get_or_create(related_pdf_file=self.pdf_file.name,
                                                                            page_id=page_id)
            if created:
                logger.info(u'PDFThumbnailerBase::get_database_pdffile_list() PDFFilePage already exists')

            if pdffilepage.pdffile_hash == file_hash:
                need_updating = False
            else:
                # Updates the hash for the PDF file
                pdffilepage.pdffile_hash = file_hash
            pdffilepage_list.append(pdffilepage)
        return pdffilepage_list, file_hash, need_updating

    def update_database(self, pdffilepage, page_id, thumbnail_image):
        """
        Adds/Updates the image file in the cache database

        :param pdffilepage: :class:`django_turnit.models.PDFFilePage` instance
        :param page_id: Page identifier
        :param thumbnail_image: thumbnail image path
        :returns: <pdffilepage>, <created>
        """
        # Creates thumbnail in database
        try:
            thumbnail_file_size = os.path.getsize(thumbnail_image)
            thumbnail_file_name = os.path.relpath(thumbnail_image, settings.MEDIA_ROOT)

            pdffilepage.param = ' '.join(self.last_args)
            pdffilepage.file_size = thumbnail_file_size
            pdffilepage.page_file.name = thumbnail_file_name
            if not self.dry_run:
                pdffilepage.save()
        except OSError as oe:
            logger.error(u'PDFThumbnailerBase::get_thumbnails() Unable to open page image file %s : %s',
                         thumbnail_image, oe)
            raise PDFThumbnailerError(u'Unable to open page image file %s' % thumbnail_image, oe)
        except IOError as ie:
            logger.error(u'PDFThumbnailerBase::get_thumbnails() Unable to open page image file %s : %s',
                         thumbnail_image, ie)
            raise PDFThumbnailerError(u'Unable to open page image file %s' % thumbnail_image, ie)
        return pdffilepage

    def get_lib_args(self, page_id):
        raise NotImplementedError


def get_page_filepath(pdf_file, page_id, guid, prefix, **kwargs):
    """
    Gets the page filepath

    :param pdf_file: file
    :param page_id: page identifier
    :param guid: globally unique identifier
    :param prefix:
    :returns:

        formatted string, from `settings.TURNIT_OUTPUT_FILE_FMT`
        (:attr:`django_turnit.conf.DjangoTurnitAppConf.OUTPUT_FILE_FMT`)
    """
    splited = os.path.basename(pdf_file.name).split('.')
    pdf_basename = '.'.join(splited[0:-1])
    fmt = settings.TURNIT_OUTPUT_FILE_FMT
    if '.gs.' in settings.TURNIT_THUMBNAILER_BACKEND:
        ext = get_ext_for_device(settings.TURNIT_GHOSTSCRIPT_IMAGE_FORMAT)
    else:
        ext = settings.TURNIT_IMAGE_EXT

    page_filepath = (fmt %
                     {'basename': pdf_basename,
                      'idx': page_id,
                      'guid': guid,
                      'param': '_'.join(['%s%s' % (k, v) for k, v in sorted(kwargs.items())]),
                      'ext': ext,
                      })
    if page_id:
        page_filepath %= page_id
    output = os.path.join(prefix, page_filepath)
    logger.debug(u'get_page_filepath() output = %s (%s)', output, type(output).__name__)
    return output


def get_ext_for_device(device_name):
    """
    Gets the image file extension from the ghostscript. See
    `Image file formats devices <http://ghostscript.com/doc/current/Devices.htm#File_formats>`_

    :param device_name: Name of the device
    :returns: extension
    """
    if 'png' in device_name:
        return 'png'
    if 'jpeg' in device_name:
        return 'jpg'
    if 'tiff' in device_name:
        return 'tif'
    if 'bmp' in device_name:
        return 'bmp'
    if 'psd' in device_name:
        return 'psd'
    if 'fax' in device_name:
        return 'fax'
    return 'png'


class PDFThumbnailerError(Exception):
    pass
