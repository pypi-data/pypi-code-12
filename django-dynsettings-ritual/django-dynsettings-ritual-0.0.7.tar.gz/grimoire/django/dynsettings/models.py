from collections import OrderedDict
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.utils.six import python_2_unicode_compatible

if 'polymorphic' not in settings.INSTALLED_APPS or \
   'django.contrib.contenttypes' not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured('For this application to work, both `polymorphic` and `django.contrib.contenttypes` '
                               'must be included in INSTALLED_APPS')

from polymorphic.models import PolymorphicModel
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from jsonfield import JSONField


@python_2_unicode_compatible
class DynamicSetting(PolymorphicModel):
    """
    A generic setting. You will be allowed to access this setting when you
    """

    name = models.CharField(max_length=255, null=False, blank=False, verbose_name=_(u'Name'),
                            validators=[RegexValidator(
                                '^[a-zA-Z_][a-zA-Z0-9_]+', _(u'Setting name must consist in a-z letters, numbers, and '
                                                             u'underscores, and cannot start with a number')
                            )], help_text=_(u'Setting name. Since it will be accessed from python code, the syntax '
                                            u'is the same as for any valid python identifier'))
    value = None
    allow_null = models.BooleanField(default=False, verbose_name=_(u'Allow null value'),
                                     help_text=_(u'Check this to allow null value in this setting.'))

    def clean(self):
        """
        Forces a value to be not-null if this setting is set to disallow null values.
        """
        if not self.allow_null and self.value is None:
            raise ValidationError({'value': _(u'This field cannot be null.')})

    def __str__(self):
        """
        The unicode value for this setting will be the setting name.
        """
        return self.name

    class Meta:
        abstract = False
        verbose_name = _(u'Dynamic Setting')
        verbose_name_plural = _(u'Dynamic Settings')


class IntegerDynamicSetting(DynamicSetting):
    """
    An integer setting. This is a regular, 4-bytes, integer (type INT in databases).
    """

    value = models.IntegerField(null=True, blank=True, verbose_name=_(u'Value'),
                                help_text=_(u'Setting value. It must be a valid (signed, 4-byte) integer value.'))

    class Meta:
        verbose_name = _(u'Integer Dynamic Setting')
        verbose_name_plural = _(u'Integer Dynamic Settings')


class BooleanDynamicSetting(DynamicSetting):
    """
    A boolean setting.
    """

    value = models.NullBooleanField(verbose_name=_(u'Value'),
                                    help_text=_(u'Setting value. It must be marked, not marked, or undefined.'))

    class Meta:
        verbose_name = _(u'Boolean Dynamic Setting')
        verbose_name_plural = _(u'Boolean Dynamic Settings')


class DecimalDynamicSetting(DynamicSetting):
    """
    A `decimal` setting (fixed precision float number). A precision is arbitrarily set to (32, 16).
    Since this record type is intended to be a system setting, more precision is not needed, and
    perhaps neither this (32, 16) precision is needed.
    """

    value = models.DecimalField(verbose_name=_(u'Value'), max_digits=32, decimal_places=16, null=True, blank=True,
                                help_text=_(u'Setting value. It must be a valid numeric value.'))

    class Meta:
        verbose_name = _(u'Decimal Dynamic Setting')
        verbose_name_plural = _(u'Decimal Dynamic Settings')


class ShortTextDynamicSetting(DynamicSetting):
    """
    A short-string (varchar) setting, with a length of 255 characters.
    """

    value = models.CharField(max_length=255, null=True, blank=True, verbose_name=_(u'Value'),
                             help_text=_(u'Setting value.'))

    class Meta:
        verbose_name = _(u'Short Text Dynamic Setting')
        verbose_name_plural = _(u'Short Text Dynamic Settings')


class LongTextDynamicSetting(DynamicSetting):
    """
    A long-text (actually, just medium text in mysql) setting.
    """

    value = models.TextField(max_length=16777215, null=True, blank=True, verbose_name=_(u'Value'),
                             help_text=_(u'Setting value.'))

    class Meta:
        verbose_name = _(u'Long Text Dynamic Setting')
        verbose_name_plural = _(u'Long Text Dynamic Settings')


class JSONDynamicSetting(DynamicSetting):
    """
    A json value setting.
    """

    value = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, null=False, blank=False, verbose_name=_(u'Value'),
                      help_text=_(u'Setting value. It must be valid JSON. This setting type is intended only for '
                                  u'developers and users who know how to compose valid JSON values. Do not edit them '
                                  u'unless you know what are you doing. If, by other means / database access, you '
                                  u'or someone corrupts the value of this field, enter by the same mean and restore '
                                  u'its original value, or just {} (open and close curly bracers) to have a valid '
                                  u'value.'))

    class Meta:
        verbose_name = _(u'JSON Dynamic Setting')
        verbose_name_plural = _(u'JSON Dynamic Settings')