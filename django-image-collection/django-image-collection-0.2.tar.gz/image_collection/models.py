"""Models for the image_collection app."""
import re
from django import forms
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

relative_url_re = re.compile(r'^[-a-zA-Z0-9_\/]+$')
validate_relative_url = RegexValidator(
    relative_url_re,
    _("Enter a valid 'relative URL' consisting of letters, numbers,"
      " underscores, forward slashes or hyphens."), 'invalid')



class RelativeURLFormField(forms.CharField):
    default_validators = [validate_relative_url]

    def clean(self, value):
        value = self.to_python(value).strip()
        return super(RelativeURLFormField, self).clean(value)


class RelativeURLField(models.fields.CharField):
    default_validators = [validate_relative_url]
    description = _("Relative URL (up to %(max_length)s)")

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 50)
        # Set db_index=True unless it's been set manually.
        if 'db_index' not in kwargs:
            kwargs['db_index'] = True
        super(RelativeURLField, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(RelativeURLField, self).deconstruct()
        if kwargs.get("max_length", None) == 50:
            del kwargs['max_length']
        if self.db_index is False:
            kwargs['db_index'] = False
        else:
            del kwargs['db_index']
        return name, path, args, kwargs

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'form_class': RelativeURLFormField}
        defaults.update(kwargs)
        return super(RelativeURLField, self).formfield(**defaults)


@python_2_unicode_compatible
class ImageCollection(models.Model):
    """
    This model wraps together a collection of images.

    :name: Human readable title for this collection
    :identifier: The unique identifier for this collection

    """

    class Meta:
        ordering = ('name', 'identifier')
        verbose_name = _('image collection')
        verbose_name_plural = _('image collections')

    name = models.CharField(
        max_length=512,
        verbose_name=_('name'),
    )

    identifier = models.SlugField(
        unique=True,
        max_length=512,
        verbose_name=_('identifier'),
    )

    def __str__(self):  # pragma: no cover
        return '{0} ({1}): {2}'.format(
            self._meta.verbose_name.title(), self.pk, self.identifier)

    def get_published_images(self):
        return self.images.filter(
            # TODO is this too complicated?
            models.Q(
                start_date__lte=now(),
                end_date__isnull=True,
            ) | models.Q(
                start_date__isnull=True,
                end_date__gte=now(),
            ) | models.Q(
                start_date__isnull=True,
                end_date__isnull=True,
            ) | models.Q(
                start_date__lte=now(),
                end_date__gte=now(),
            )
        ).distinct()

    def is_public(self):
        """Returns True, if any image exists, that is currently published."""
        return self.get_published_images().exists()


@python_2_unicode_compatible
class ImageSlide(models.Model):
    """
    One image object and its extra meta information.

    :collection: The collection this image belongs to
    :image: The image file
    :image_mobile: Optional alternative image to be used for mobile devices
    :alt_text: What goes into the alt attribute
    :link: If the image should link to any specific URL, put it here. Best is
      to use the ``url`` property instead of this, since that falls back to the
      image url automatically.
    :mobile_link: If this collection is loaded on a mobile app, you might
      want to link to an in-app route instead of a URL.
    :is_visible_on_mobile: Set this to true if this slide should be shown
      in a mobile app.
    :data-class: Optional. If you want to attach click events to this image,
      fill out this field.
    :start_date: The datetime, where the image should start to be published
    :start_end: The datetime, where the image should no longer be published

    """

    class Meta:
        ordering = ('collection', 'start_date', 'end_date', 'alt_text')
        verbose_name = _('image')
        verbose_name_plural = _('images')

    update_date = models.DateTimeField(
        verbose_name=_('update date'),
        auto_now=True, null=True, blank=True,
    )

    collection = models.ForeignKey(
        ImageCollection,
        verbose_name=_('image collection'),
        related_name='images',
    )

    image = models.ImageField(
        upload_to='image_slides',
        verbose_name=_('image'),
    )

    image_mobile = models.ImageField(
        upload_to='image_slides',
        verbose_name=_('image_mobile'),
        blank=True,
        null=True,
    )

    caption_headline = models.CharField(
        max_length=256,
        verbose_name=_('caption headline'),
        help_text=_('This text is displayed as title of the image.'),
        blank=True,
    )

    caption = models.CharField(
        max_length=512,
        verbose_name=_('caption'),
        help_text=_('This text is displayed as description of the image.'),
        blank=True,
    )

    alt_text = models.CharField(
        max_length=128,
        verbose_name=_('alt text'),
        help_text=_('This will go into the ``alt`` attribute of the image\'s'
                    ' HTML markup.'),
        blank=True,
    )

    external_link = models.URLField(
        verbose_name=_('external link'),
        help_text=_('E.g. "http://www.example.com/my-page/". Enter absolute'
                    ' URL, that the image should link to.'),
        blank=True,
    )

    internal_link = RelativeURLField(
        verbose_name=_('internal link'),
        help_text=_('E.g. "/my-page/". Enter slug of internal pager, that the'
                    ' image should link to.'),
        blank=True,
    )

    mobile_link = models.CharField(
        max_length=4000,
        verbose_name=_('mobile link'),
        help_text=_(
            'i.e. "{route: "shop/cateogry", categoryName: "artworks"}"'),
        blank=True,
    )

    is_visible_on_mobile = models.BooleanField(default=False)

    data_class = models.CharField(
        verbose_name=_('data class'),
        max_length=512,
        help_text=(
            'Set this if you want to handle click events on this image via'
            ' JavaScript.'),
        blank=True
    )

    start_date = models.DateTimeField(
        verbose_name=_('publish date'),
        blank=True, null=True,
    )

    end_date = models.DateTimeField(
        verbose_name=_('unpublish date'),
        blank=True, null=True,
    )

    generic_position = GenericRelation(
        'generic_positions.ObjectPosition'
    )

    def __str__(self):  # pragma: no cover
        return '{0} ({1}): {2}'.format(
            self._meta.verbose_name.title(), self.pk, self.alt_text)

    def clean(self):
        if self.internal_link and self.external_link:
            raise ValidationError(_('You cannot have both and internal and an'
                                    ' external link. Please remove at least'
                                    ' one.'))

    @property
    def url(self):  # pragma: no cover
        """Should always return a proper url."""
        return self.external_link.strip() or self.internal_link.strip() \
            or self.image.url

    @url.setter
    def url(self, value):  # pragma: no cover
        self.link = value

    @url.deleter
    def url(self):  # pragma: no cover
        self.link = ''
