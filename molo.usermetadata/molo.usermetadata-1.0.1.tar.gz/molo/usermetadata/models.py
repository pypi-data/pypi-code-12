
from django.db import models
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.contrib.settings.models import BaseSetting, register_setting

from molo.core.models import TranslatablePageMixin


@register_setting
class PersonaeSettings(BaseSetting):
    persona_required = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Activate Personae"),
    )


class PersonaIndexPage(Page):
    parent_page_types = []
    subpage_types = ['PersonaPage']


class PersonaPage(TranslatablePageMixin, Page):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    class Meta:
        verbose_name = _('Persona')
        verbose_name_plural = _('Personae')

PersonaPage.content_panels = [
    FieldPanel('title', classname='full title'),
    ImageChooserPanel('image'),
]
