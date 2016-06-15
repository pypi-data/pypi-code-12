"""
Models for :mod:`django-turnit` application
"""
import logging

from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from django_turnit.utilities import get_file_field_from_id, get_id_from_field_file
# noinspection PyUnresolvedReferences
from django_turnit.conf import DjangoTurnitAppConf

logger = logging.getLogger('django_turnit.models')


def upload_pdf_image_thumbnail(instance, filename):
    """
    Sets the path to upload to for PDF page thumbnails

    :param instance: instance
    :param filename: file name
    :returns: upload file path
    """
    return '%s/%s' % (settings.TURNIT_OUTPUT_MEDIA_ROOT, filename)


@python_2_unicode_compatible
class PDFFilePage(models.Model):
    """
    Pages included in the PDF file
    """
    #: Image file containing the thumbnailed page as a PNG file
    page_file = models.ImageField(verbose_name=_('PDF File page'), upload_to=upload_pdf_image_thumbnail)

    #: Page number in the PDF file
    page_id = models.PositiveIntegerField(verbose_name=_('Page id'), default=1)

    #: related file as `<app>.<model_name>.<id>.<field_name>` string
    related_pdf_field = models.CharField(verbose_name=_('Related PDF file field'), max_length=255)

    #: path to the related file
    related_pdf_file = models.CharField(verbose_name=_('Related PDF file path'), max_length=512)

    #: file size
    file_size = models.PositiveIntegerField(verbose_name=_("File size"), null=True, blank=True)

    #: parameters used to build the image
    param = models.CharField(verbose_name=_('PDF Generation parameter'), max_length=255, null=True, blank=True)

    pdffile_hash = models.CharField(verbose_name=_('Hash of the PDF file'), max_length=512, null=True, blank=True)

    def get_related_field_file(self):
        """
        Reads the :attr:`models.PDFFilePage.related_pdf_file` and re-build the FileField instance

        :returns: related file field
        """
        field_file = get_file_field_from_id(self.related_pdf_file, strict=True)
        return field_file

    class Meta:
        ordering = ('related_pdf_file', 'page_id', )
        verbose_name = _('PDF file page')
        verbose_name_plural = _('PDF file pages')

    def __str__(self):
        # noinspection PyStringFormat
        return '%s [#%04d]' % (self.related_pdf_file, self.page_id)
