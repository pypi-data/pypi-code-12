# coding=utf-8
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(u"创建时间", auto_now_add=True, null=True, blank=True, editable=False)
    modified_at = models.DateTimeField(u"修改时间", auto_now=True, null=True, blank=True, editable=False)

    class Meta:
        abstract = True
