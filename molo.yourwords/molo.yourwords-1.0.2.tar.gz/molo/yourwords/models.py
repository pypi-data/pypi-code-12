from django.db import models
from django.utils.translation import ugettext_lazy as _


from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, StreamFieldPanel, FieldRowPanel,
    MultiFieldPanel)
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel

from molo.core.blocks import MarkDownBlock
from molo.core.models import ArticlePage, TranslatablePageMixin


class YourWordsCompetitionIndexPage(Page):
    parent_page_types = []
    subpage_types = ['yourwords.YourWordsCompetition']


class YourWordsCompetition(TranslatablePageMixin, Page):
    subpage_types = ['yourwords.TermsAndConditions', 'yourwords.ThankYou']
    description = models.TextField(null=True, blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content = StreamField([
        ('heading', blocks.CharBlock(classname="full title")),
        ('paragraph', MarkDownBlock()),
        ('image', ImageChooserBlock()),
        ('list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('numbered_list', blocks.ListBlock(blocks.CharBlock(label="Item"))),
        ('page', blocks.PageChooserBlock()),
    ], null=True, blank=True)

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    extra_style_hints = models.TextField(
        default='',
        null=True, blank=True,
        help_text=_(
            "Styling options that can be applied to this section "
            "and all its descendants"))

    def get_effective_extra_style_hints(self):
            return self.extra_style_hints

    def get_effective_image(self):
        return self.image

    def thank_you_page(self):
        qs = ThankYou.objects.live().child_of(self)
        if qs.exists():
            return qs.last()
        return None

    class Meta:
        verbose_name = 'YourWords Competition'
        verbose_name_plural = 'YourWords Competitions'


YourWordsCompetition.content_panels = [
    FieldPanel('title', classname='full title'),
    FieldPanel('description'),
    ImageChooserPanel('image'),
    StreamFieldPanel('content'),
    MultiFieldPanel(
        [
            FieldPanel('start_date'),
            FieldPanel('end_date'),
        ],
        heading="Your Words Competition Settings",)
]

YourWordsCompetition.settings_panels = [
    MultiFieldPanel(
        [FieldRowPanel(
            [FieldPanel('extra_style_hints')], classname="label-above")],
        "Meta")
]


class YourWordsCompetitionEntry(models.Model):
    competition = models.ForeignKey(YourWordsCompetition)
    submission_date = models.DateField(null=True, blank=True,
                                       auto_now_add=True)
    user = models.ForeignKey('auth.User')
    story_name = models.CharField(max_length=128)
    story_text = models.TextField()
    terms_or_conditions_approved = models.BooleanField()
    hide_real_name = models.BooleanField()
    is_read = models.BooleanField(default=False)
    is_shortlisted = models.BooleanField(default=False)
    is_winner = models.BooleanField(default=False)

    article_page = models.ForeignKey(
        'core.ArticlePage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text=_('Page to which the entry was converted to')
    )

    class Meta:
        verbose_name = 'YourWords Competition Entry'
        verbose_name_plural = 'YourWords Competition Entries'


class TermsAndConditions(ArticlePage):
    subpage_types = []

    def get_parent_page(self):
        return YourWordsCompetition.objects.all().ancestor_of(self).last()


class ThankYou(ArticlePage):
    subpage_types = []

    def get_parent_page(self):
        return YourWordsCompetition.objects.all().ancestor_of(self).last()
