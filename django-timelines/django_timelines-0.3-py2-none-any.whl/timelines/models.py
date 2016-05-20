# -*- coding: utf-8 -*-
try:
    from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
except ImportError:
    from django.contrib.contenttypes.generic import GenericRelation, GenericForeignKey
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.contrib.contenttypes.models import ContentType

from concepts.models import delete_listener, ConceptItem
from taggit.managers import TaggableManager
from credits.models import CreditGroup

from .fields import HistoricalDateField, HistoricalDate, ColorField
from .registration import registry
from .settings import CLICK_THROUGH_TEMPLATE, BACKGROUND_IMAGE_RELATED_FIELD
import swapper

ADAPTER_CTYPES = [ContentType.get_for_instance(x).id for x in registry._registry]


class BaseSlide(models.Model):
    """
    Handles the adapting for both the title slide (part of the Timeline model)
    and the normal Slide model.
    """
    overrides = ['headline', 'text', 'credit', 'caption', 'media_url', 'clickthrough_url', 'thumbnail']

    url = models.CharField(
        _('media URL'),
        max_length=255,
        blank=True, null=True)
    content_type = models.ForeignKey(ContentType,
        verbose_name=_('media content type'),
        related_name='+',
        blank=True, null=True)
    object_id = models.PositiveIntegerField(
        _('media ID'),
        blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    use_media_as_background = models.BooleanField(
        _('use media as background'),
        default=False)
    background_image = models.ForeignKey(
        swapper.get_model_name('timelines', 'background_image'),
        blank=True, null=True,
        verbose_name=_('background image'))
    background_color = ColorField(
        _('background color'),
        default="ffffff",)

    headline_ovr = models.CharField(
        _('headline'),
        max_length=255,
        blank=True, null=True,
        help_text="Used for URL or override for selected object.")
    text_ovr = models.TextField(
        _('text'),
        blank=True, null=True,
        help_text="Used for URL or override for selected object.")
    credit_ovr = models.CharField(
        _("credit"),
        max_length=255,
        null=True, blank=True,
        help_text="Used for URL or override for selected object.")
    caption_ovr = models.TextField(
        _("caption"),
        null=True, blank=True,
        help_text="Used for URL or override for selected object.")

    @property
    def adapter(self):
        if hasattr(self, '_adapter'):
            return self._adapter
        self._adapter = registry.adapter_for_instance(self.content_object)
        return self._adapter

    def get_media_url(self):
        return self.url or self.media_url

    def get_background(self):
        if self.use_media_as_background:
            return {
                'url': self.get_media_url()
            }
        elif self.background_image:
            return {
                'url': getattr(self.background_image,
                                 BACKGROUND_IMAGE_RELATED_FIELD).url
            }
        return {
            'color': self.background_color
        }

    def get_media(self):
        if self.use_media_as_background:
            return None

        media = {
            'url': self.get_media_url(),
            'caption': self.caption,
            'credit': self.credit,
        }
        if self.adapter and self.adapter.thumbnail:
            media['thumbnail'] = self.adapter.thumbnail
        return media

    def __getattr__(self, name):
        """
        Return either the overridden value, or the original value, or raise
        and AttributeError.
        """
        if name in self.overrides:
            adapter = registry.adapter_for_instance(self.content_object)
            value = getattr(self, "%s_ovr" % name, "--NOVALUE--")
            if value != "--NOVALUE--" and value:
                return value
            if hasattr(self, "content_object") and self.content_object:
                return getattr(adapter, name, '')
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    class Meta:
        abstract = True


class Era(models.Model):
    """
    Era objects are JSON objects which are used to label a span of time on the
    timeline navigation component. In structure, they are essentially very
    restricted "slide" objects.
    """
    start_date = HistoricalDateField(verbose_name=_('start date'))
    end_date = HistoricalDateField(verbose_name=_('end date'))
    headline = models.CharField(verbose_name=_('label'), max_length=255, blank=True)

    class Meta:
        verbose_name = _("Era")
        verbose_name_plural = _("Eras")
        ordering = ('timeline', 'start_date', )

    def date_string(self):
        """
        Format the dates into a string representation
        """
        return u"%s - %s" % (
            HistoricalDate(self.start_date).__unicode__(),
            HistoricalDate(self.end_date).__unicode__())

    def to_dict(self):
        output = {
            'start_date': HistoricalDate(self.start_date).to_dict(),
            'end_date': HistoricalDate(self.end_date).to_dict(),
            'text': {}
        }
        if self.headline:
            output['text']['headline'] = self.headline
        return output

    def __unicode__(self):
        data = self.to_dict()
        output = u"%s - %s" % (
            HistoricalDate(self.start_date).__unicode__(),
            HistoricalDate(self.end_date).__unicode__())
        if 'text' in data:
            return u'%s: %s' % (data['text']['headline'], output)
        return output


class Slide(BaseSlide):
    start_date = HistoricalDateField(_('start date'))
    start_time = models.TimeField(
        _('start time'),
        blank=True, null=True)
    end_date = HistoricalDateField(
        _('end date'),
        blank=True, null=True)
    end_time = models.TimeField(
        _('end time'),
        blank=True, null=True)

    def __unicode__(self):
        if self.url:
            return u"URL: %s" % self.url
        else:
            return u"Object: %s" % self.content_object

    class Meta:
        verbose_name = _("Slide")
        verbose_name_plural = _("Slides")
        ordering = ('start_date', 'start_time', )

    @property
    def date_string(self):
        """
        Format the dates into a string representation
        """
        startdate = HistoricalDate(self.start_date).__unicode__()

        if self.end_date:
            return "%s - %s" % (startdate, HistoricalDate(self.end_date).__unicode__())
        return startdate

    def to_dict(self):
        click_through = ''
        click_through_url = self.adapter.get_clickthrough_url()
        if click_through_url:
            click_through = CLICK_THROUGH_TEMPLATE % click_through_url

        output = {
            'start_date': HistoricalDate(self.start_date).to_dict(),
            'text': {
                'headline': self.headline,
                'text': '%s%s' % (self.text, click_through)
            },
            'background': self.get_background()
        }

        if self.end_date:
            output['end_date'] = HistoricalDate(self.end_date).to_dict()
        if self.start_time:
            output['start_date']['hour'] = self.start_time.hour
            output['start_date']['minute'] = self.start_time.minute
            output['start_date']['second'] = self.start_time.second
        if self.end_time:
            output['end_date']['hour'] = self.end_time.hour
            output['end_date']['minute'] = self.end_time.minute
            output['end_date']['second'] = self.end_time.second

        if not self.use_media_as_background:
            output['media'] = self.get_media()

        return output


class TimelineSlide(models.Model):
    timeline = models.ForeignKey('Timeline', related_name="events")
    slide = models.ForeignKey(Slide)
    order = models.PositiveIntegerField(
        _("order"),
        default="1",
        help_text=_("Used to order within the same date."))
    group = models.CharField(
        _('group'),
        max_length=255,
        blank=True, null=True,
        help_text=_('If present, Timeline will organize events with the same value for group to be in the same row or adjacent rows, separate from events in other groups.'))

    def to_dict(self):
        output = self.slide.to_dict()
        if self.group:
            output['group'] = self.group

        return output

    class Meta:
        verbose_name = "Timeline Slide"
        verbose_name_plural = "Timeline Slides"
        ordering = ('timeline', 'slide__start_date', 'slide__start_time', 'order')


class Timeline(BaseSlide):
    scale = models.CharField(
        _('scale'),
        max_length=15,
        choices=(
            ('human', _('human')),
            ('cosmological', _('cosmological')),
        ),
        default='human',
        help_text=_('The cosmological scale is required to handle dates in the very distant past or future.')
    )
    slug = models.SlugField(
        _('slug'),
        max_length=255,
        default='',
        help_text=_('Slug must be set manually if headline is not set.'))
    description = models.TextField(_('description'),
        blank=True, null=True,
        help_text=_("This content appears in metadata and search."))
    content = models.TextField(_('content'), blank=True, null=True)
    slides = models.ManyToManyField(Slide, through='TimelineSlide')
    eras = models.ManyToManyField(Era, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    published = models.BooleanField(
        _('published'),
        default=False)
    publish_date = models.DateTimeField(
        _('publish date'),
        blank=True, null=True)
    concept_items = GenericRelation(ConceptItem)
    concepts = TaggableManager(through=ConceptItem)
    credits = models.ForeignKey(
        CreditGroup,
        verbose_name=_("timeline credits"),
        blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.published:
            self.publish_date = now()
        else:
            self.publish_date = None

        super(Timeline, self).save(*args, **kwargs)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse
        return reverse('timeline-detail', args=[str(self.slug)])

    def get_preview_url(self):
        from django.core.urlresolvers import reverse
        return reverse('timeline-detail-preview', args=[str(self.slug)])

    def to_dict(self):
        output = {
            'title': {
                'text': {
                    'headline': self.headline,
                    'text': self.text,
                },
                'media': self.get_media(),
                'background': self.get_background()
            },
            'unique_id': self.slug,
            'scale': self.get_scale_display(),
            'eras': [],
            'events': [],
        }

        for era in self.eras.all():
            output['eras'].append(era.to_dict())
        for event in self.events.all():
            output['events'].append(event.to_dict())
        return output

    def __unicode__(self):
        return self.headline


models.signals.post_delete.connect(delete_listener, sender=Timeline)
