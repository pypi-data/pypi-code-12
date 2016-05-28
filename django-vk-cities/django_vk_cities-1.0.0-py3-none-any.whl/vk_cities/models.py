# coding=utf-8

from django.db import models
from django.utils.translation import ugettext as _


class VKPlace(models.Model):

    """Abstract model for VK.com places."""

    vk_id = models.PositiveIntegerField(editable=False, unique=True)
    name = models.CharField(_('Name'), max_length=255)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class Country(VKPlace):

    """VK.com country."""

    class Meta:
        verbose_name = _('Country')
        verbose_name_plural = _('Countries')


class Region(VKPlace):

    """VK.com country region."""

    country = models.ForeignKey(
        Country, related_name='regions', verbose_name=_('Country')
    )

    class Meta:
        verbose_name = _('Region')
        verbose_name_plural = _('Regions')


class City(VKPlace):

    """VK.com city."""

    region = models.ForeignKey(
        Region, related_name='cities', verbose_name=_('Region')
    )
    area = models.CharField(_('Area'), max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
