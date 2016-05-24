from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic


class MetaContent(models.Model):
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (
            ('content_type', 'object_id'),
        )

    def __unicode__(self):
        return u'Meta'


class URLMetaContent(models.Model):
    url = models.CharField('URL', max_length=200, unique=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    class Meta:
        verbose_name = 'URL meta content'

    def __unicode__(self):
        return self.url
