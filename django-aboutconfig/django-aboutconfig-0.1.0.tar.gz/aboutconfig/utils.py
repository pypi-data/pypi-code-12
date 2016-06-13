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
    return CACHE_KEY_PREFIX + key.lower()


def _get_cache():
    return caches[settings.ABOUTCONFIG_CACHE_NAME]


def _set_cache(config):
    cache = _get_cache()
    cache_key = _cache_key_transform(config.key)
    cache.set(cache_key, DataTuple(config.get_value(), config.allow_template_use),
              settings.ABOUTCONFIG_CACHE_TTL)


def load_serializer(class_path):
    split_path = class_path.split('.')
    class_name = split_path.pop()
    module_path = '.'.join(split_path)

    module = importlib.import_module(module_path)
    klass = getattr(module, class_name)

    if not BaseSerializer.is_class_valid(klass):
        raise ValueError('"{}" is not a valid serializer'.format(class_path))

    return klass


def serializer_validator(class_path):
    try:
        load_serializer(class_path)
    except (ValueError, ImportError, AttributeError):
        raise ValidationError('Invalid serializer class')


def get_config(key, value_only=True):
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
    from .models import Config

    for config in Config.objects.all():
        _set_cache(config)
