"""Common utilities used by the module."""

import importlib
from collections import namedtuple

from django.core.exceptions import ValidationError
from django.core.cache import caches
from django.conf import settings

from .serializers import BaseSerializer
from .constants import CACHE_KEY_PREFIX

_SENTINEL = object()
DataTuple = namedtuple('DataTuple', 'value,allow_template_use')


def _cache_key_transform(key):
    """Transforms the configuration key to avoid undesired collisions in cache."""

    return CACHE_KEY_PREFIX + key.lower()


def _get_cache():
    """Return the configured cache backend."""

    return caches[settings.ABOUTCONFIG_CACHE_NAME]


def _set_cache(config):
    """Put the given configuration data into cache."""

    cache = _get_cache()
    cache_key = _cache_key_transform(config.key)
    cache.set(cache_key, DataTuple(config.get_value(), config.allow_template_use),
              settings.ABOUTCONFIG_CACHE_TTL)


def load_serializer(class_path):
    """Load a class by name/path that implements the serialization interface.

    Returns an instance of the class or raises ImportError/ValueError/AttributeError."""

    split_path = class_path.split('.')
    class_name = split_path.pop()
    module_path = '.'.join(split_path)

    module = importlib.import_module(module_path)
    klass = getattr(module, class_name)

    if not BaseSerializer.is_class_valid(klass):
        raise ValueError('"{}" is not a valid serializer'.format(class_path))

    return klass


def serializer_validator(class_path):
    """Check whether the given class (via path) is a valid serialzier or not.

    Raises ValidationError if not valid."""

    try:
        load_serializer(class_path)
    except (ValueError, ImportError, AttributeError):
        raise ValidationError('Invalid serializer class')


def get_config(key, value_only=True):
    """Get the configuration value for the given key.

    By default this function only returns the value, set value_only=False to get a
    2-tuple with the following elements: (value, allow_template_use). This functionality
    is almost certainly not needed by end-users, only included for the built-in template
    tag filtering functionality.

    Returns None if no such configuration exists (or (None, True) if value_only=False)."""

    from .models import Config

    cache = _get_cache()
    cache_key = _cache_key_transform(key)
    data = cache.get(cache_key, _SENTINEL)

    if data is _SENTINEL:
        try:
            config = Config.objects.get(key=key.lower())
        except Config.DoesNotExist:
            data = DataTuple(None, True)
            cache.set(cache_key, data, settings.ABOUTCONFIG_CACHE_TTL)
        else:
            data = DataTuple(config.get_value(), config.allow_template_use)
            _set_cache(config)

    return data.value if value_only else data


def preload_cache():
    """Load all configuration data into cache."""

    from .models import Config

    for config in Config.objects.all():
        _set_cache(config)
