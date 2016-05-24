# -*- coding: utf-8 -*-
from congo.conf import settings
from congo.utils.fields import MultisizeImageField
from congo.utils.mixins import PositionMixin
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
import os
import re

def get_watermark_choice():
    watermark_choice_path = settings.CONGO_WATERMARK_PATH
    if watermark_choice_path:
        return [(filename, filename) for filename in os.listdir(watermark_choice_path) if re.match("^([a-z_]+).png$", filename, re.IGNORECASE)]
    return []

@python_2_unicode_compatible
class AbstractPhoto(PositionMixin):
    title = models.CharField(_("Title"), blank = True, null = True, max_length = 255)
    image = MultisizeImageField(watermark_field = 'watermark', width_field = 'width', height_field = 'height', max_length = 255, verbose_name = _("Image file"))
    width = models.IntegerField(_("Width"))
    height = models.IntegerField(_("Height"))
    watermark = models.CharField(_("Watermark"), max_length = 50, null = True, blank = True, choices = get_watermark_choice())
    is_visible = models.BooleanField(_("Is visible"), default = True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(AbstractPhoto, self).__init__(*args, **kwargs)
        self._watermark = self.watermark
        if not hasattr(self.image, '_dimensions_cache'):
            self.image._dimensions_cache = (self.width, self.height)

    def  __str__(self):
        if self.title:
            return self.title
        else:
            split = self.image.name.split('/')
            return split[-1]

    def get_size(self):
        if self.width and self.height:
            return (self.width, self.height)
        else:
            return None

    def delete(self, *args, **kwargs):
        self.image._delete_resized()

        storage, path = self.image.storage, self.image.path
        super(AbstractPhoto, self).delete(*args, **kwargs)
        storage.delete(path)

    def save(self, *args, **kwargs):
        if self._watermark != self.watermark:
            self.image._delete_resized()

        super(AbstractPhoto, self).save(*args, **kwargs)
