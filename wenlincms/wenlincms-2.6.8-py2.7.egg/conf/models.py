# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from wenlincms.core.models import SiteRelated


@python_2_unicode_compatible
class Setting(SiteRelated):
    """
    Stores values for ``wenlincms.conf`` that can be edited via the admin.
    """

    name = models.CharField(max_length=50)
    value = models.TextField()

    class Meta:
        verbose_name = "系统设置"
        verbose_name_plural = "系统设置"

    def __str__(self):
        return "%s: %s" % (self.name, self.value)
