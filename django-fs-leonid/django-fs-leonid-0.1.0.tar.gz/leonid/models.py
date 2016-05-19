# coding=utf-8

from os import path

from django.db import models
from django.utils.translation import ugettext_lazy as _

from . import settings as _settings


class LeonidFile(models.Model):
    name = models.CharField(verbose_name=_(u'name'), max_length=100, unique=True)
    content = models.TextField(verbose_name=_(u'content'), blank=True, default=u'')

    class Meta:
        verbose_name = _(u'leonid file')
        verbose_name_plural = _(u'leonid files')
        ordering = ('name',)

    def __unicode__(self):
        return u'{0}'.format(self.name)

    @property
    def content_type(self):
        _, ext = path.splitext(self.name)
        ext = ext.lstrip(u'.')
        return _settings.EXTENSION_CONTENT_TYPE_MAP.get(ext)
