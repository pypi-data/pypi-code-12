# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from cms.models import CMSPlugin


@python_2_unicode_compatible
class HTTPHeader(models.Model):
    header_name = models.CharField(_('header name'), max_length=250, blank=False, default='')

    def __str__(self):
        return self.header_name


@python_2_unicode_compatible
class HeaderControlPluginModel(CMSPlugin):
    cache_duration = models.PositiveIntegerField(
        _('cache duration'), default=60, help_text=_('Provide the duration (in seconds) that this content should be considered valid.'))
    headers = models.ManyToManyField(HTTPHeader, blank=True, default=None)

    def __str__(self):
        headers = ", ".join(self.headers.all().values_list('header_name', flat=True))
        if len(headers) > 32:
            headers = headers[:30] + "..."
        return "Expire in {0}s. Vary on: {1}".format(self.cache_duration, headers)

    def copy_relations(self, old_instance):
        self.headers = old_instance.headers.all()

