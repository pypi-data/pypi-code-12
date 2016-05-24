from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


class BaseMeta(models.Model):
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

    open_graph_url = models.URLField('URL', blank=True, help_text='Canonical URL')
    open_graph_title = models.CharField('Title', max_length=100, blank=True)
    open_graph_description = models.TextField('Description', blank=True)
    open_graph_image = models.ImageField(
        'Image', upload_to='blancseo/meta', blank=True,
        width_field='open_graph_image_width', height_field='open_graph_image_height',
        help_text='1.91:1 aspect ratio, ideally 1200 x 630 or 600 x 315')
    open_graph_image_width = models.PositiveIntegerField(null=True, editable=False)
    open_graph_image_height = models.PositiveIntegerField(null=True, editable=False)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class MetaContent(BaseMeta):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (
            ('content_type', 'object_id'),
        )

    def __str__(self):
        return 'Meta'

    @property
    def og_title(self):
        return self.open_graph_title or self.title

    @property
    def og_description(self):
        return self.open_graph_description or self.description


@python_2_unicode_compatible
class URLMetaContent(BaseMeta):
    url = models.CharField(
        'URL', max_length=200, unique=True,
        help_text='Page URL without protocol or domain, eg. /about/')

    class Meta:
        verbose_name = 'URL meta content'

    def __str__(self):
        return self.url
