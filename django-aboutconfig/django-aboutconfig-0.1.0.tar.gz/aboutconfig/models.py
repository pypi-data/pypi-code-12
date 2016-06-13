from django.db import models
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.encoding import python_2_unicode_compatible

from .constants import KEY_REGEX
from . import utils


@python_2_unicode_compatible
class DataType(models.Model):
    name = models.CharField(max_length=32)
    serializer_class = models.CharField(
        max_length=256, validators=[utils.serializer_validator],
        help_text='Must be a class that implements serialize, unserialize and validate methods.')

    def get_class(self):
        return utils.load_serializer(self.serializer_class)


    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Config(models.Model):
    key = models.CharField(
        max_length=512, validators=[RegexValidator(KEY_REGEX)], unique=True,
        help_text='Period separated strings. All keys are case-insensitive.')
    value = models.CharField(max_length=1024, blank=True, null=True)
    data_type = models.ForeignKey(DataType, related_name='+')
    default_value = models.CharField(
        max_length=1024, editable=False,
        help_text='Default value set by setting provider. Used by 3rd-party apps.')
    allow_template_use = models.BooleanField(default=True,
                                             help_text='Prevent settings from being accessible ' \
                                                       'via the template filter. Can ' \
                                                       'be useful for API-keys, for example')


    def save(self, **kwargs):
        self.key = self.key.lower()
        super(Config, self).save(**kwargs) # pylint: disable=no-member


    def full_clean(self, **kwargs):
        super(Config, self).full_clean(**kwargs) # pylint: disable=no-member

        try:
            self._get_serializer().validate(self.value)
        except ValidationError as e:
            raise ValidationError({'value': e})


    def get_raw_value(self):
        """Get serialized value.

        Tries to get manually set value before falling back to default value."""

        if self.value is None:
            return self.default_value
        else:
            return self.value


    def get_value(self):
        """Get unserialized value."""

        return self._get_serializer().unserialize(self.get_raw_value())


    def set_value(self, val):
        self.value = self._get_serializer().serialize(val)


    def _get_serializer(self):
        return self.data_type.get_class()(self)


    def in_cache(self):
        return utils.get_config(self.key) is not None
    in_cache.boolean = True # django admin icon fix


    def __str__(self):
        return '{}={}'.format(self.key, self.get_raw_value())


@receiver(models.signals.post_save, sender=Config)
def update_cache(sender, instance, **kwargs):
    utils._set_cache(instance)
