"""Database models used by this module."""

from django.db import models
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.encoding import python_2_unicode_compatible

from .constants import KEY_REGEX
from . import utils


__all__ = ('DataType', 'Config')


@python_2_unicode_compatible
class DataType(models.Model):
    """
    Model representing the data type.

    Each model instance is associated with a serializer class that performs the casting
    of python objects to strings and back.
    """

    name = models.CharField(max_length=32)
    serializer_class = models.CharField(
        max_length=256, validators=[utils.serializer_validator],
        help_text='Must be a class that implements serialize, unserialize and validate methods.')

    def get_class(self):
        """Load and the configured serializer class."""

        return utils.load_serializer(self.serializer_class)


    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Config(models.Model):
    """
    Model representing the user-defined configuration data.

    Most of the time just key, value and data_type need to be set. The default_value field is
    used for by 3rd-party applications that rely on this module that require that some sane value
    is set in the configuration. Users can override this if wish, but the default value remains.

    The allow_template_use field is only used in the get_config template filter. There are times
    when you have some sensitive configuration stored, but want to prevent it from potentially
    leaking out via user-configurable templates. If the value is set to false, the filter will act
    as if the configuration does not exist at all.

    Note: an empty string is equivalent to None, and the configuration will fall back to the
    default value.
    """

    EMPTY_VALUES = (None, '')

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
        """Save model to database."""

        self.key = self.key.lower()
        super(Config, self).save(**kwargs) # pylint: disable=no-member


    def full_clean(self, **kwargs):
        """Validate model data before saving."""

        super(Config, self).full_clean(**kwargs) # pylint: disable=no-member

        if self.value in self.EMPTY_VALUES:
            self.value = None

            if self.default_value is None:
                raise ValidationError({'value': ValidationError('A value is required')})
            else:
                # have default value to fall back on
                return

        try:
            self._get_serializer().validate(self.value)
        except ValidationError as e:
            raise ValidationError({'value': e})


    def get_raw_value(self):
        """
        Get serialized value.

        Tries to get manually set value before falling back to default value.
        """

        if self.value in self.EMPTY_VALUES:
            return self.default_value
        else:
            return self.value


    def get_value(self):
        """Get unserialized value."""

        return self._get_serializer().unserialize(self.get_raw_value())


    def set_value(self, val):
        """Set the configuration value via a python object. Takes care of the serialization."""

        self.value = self._get_serializer().serialize(val)


    def _get_serializer(self):
        """Get the configured serializer class instance."""

        return self.data_type.get_class()(self)


    def in_cache(self):
        """
        Check if the configuration value is already present in cache.

        Works like a python get_config() call - ignores allow_template_use setting.
        """

        return utils.get_config(self.key) is not None
    in_cache.boolean = True # django admin icon fix


    def __str__(self):
        return '{}={}'.format(self.key, self.get_raw_value())


# pylint: disable=unused-argument
@receiver(models.signals.post_save, sender=Config)
def update_cache(sender, instance, **kwargs):
    """
    Update cache for the given configuration instance.

    Automatically called on configuration creation/update.
    """

    # pylint: disable=protected-access
    utils._set_cache(instance)
