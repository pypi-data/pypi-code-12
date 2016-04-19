from django.core.exceptions import ValidationError
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from mptt.fields import TreeForeignKey

from glitter.pages.models import Page
from glitter.models import BaseBlock


class RelatedPagesBlock(BaseBlock):
    title = models.CharField(max_length=100, blank=True, help_text='Defaults to "Related pages"')

    render_function = 'glitter.blocks.related_pages.views.relatedpages_view'

    class Meta:
        verbose_name = 'related pages'


@python_2_unicode_compatible
class RelatedPage(models.Model):
    related_pages_block = models.ForeignKey(RelatedPagesBlock)
    title = models.CharField(
        max_length=100, blank=True, help_text='Optional for pages, required for links')
    page = TreeForeignKey(Page, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        ordering = ('position',)

    def __str__(self):
        return str(self.page)

    def clean(self):
        if not self.page and not self.link:
            raise ValidationError('Need a page or a link')

        if self.page and self.link:
            raise ValidationError('Need a page or a link, not both')

        if self.link and not self.title:
            raise ValidationError('Need a title for a link')
