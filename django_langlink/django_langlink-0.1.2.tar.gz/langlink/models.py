from __future__ import unicode_literals

from django.db import models


class Language(models.Model):
    is_langlink_model = True
    code = models.CharField(max_length=2, unique=True)
    title = models.CharField(max_length=80)
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['title']

    def __unicode__(self):
        return self.title
