from django.db import models
from django.core.urlresolvers import reverse

from mauveinternet.markdown.util import MarkdownTextField

class HelpTextManager(models.Manager):
    def get_query_set(self):
        return super(HelpTextManager, self).get_query_set().exclude(description='')


class InlineHelp(models.Model):
    slug = models.SlugField()
    description = MarkdownTextField(blank=True, help_text="This field may be formatted with Markdown.")

    objects = models.Manager()
    texts = HelpTextManager()

    def __unicode__(self):
        return self.slug

    def get_absolute_url(self):
        return reverse('quick-help', kwargs={'slug': self.slug})

    def has_description(self):
        return bool(self.description)

    class Admin:
        list_display = ['__unicode__', 'has_description']

    class Meta:
        verbose_name_plural = u'inline help'
