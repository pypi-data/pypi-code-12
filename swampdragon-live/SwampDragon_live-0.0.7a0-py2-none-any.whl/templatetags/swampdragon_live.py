# -*- coding: utf-8 -*-
from django.core.cache import InvalidCacheBackendError, caches
from django.contrib.contenttypes.models import ContentType
from django.template.loader import get_template
from django.template import Library
from django.db.models.query import QuerySet
from django.db.models import Model
import hashlib

from ..utils import get_channel_cache
from ..classes import ModelInstanceRef
from ..classes import ModelQuerySetRef
from ..classes import ContextRef

register = Library()

def get_ref_for_instance(instance):
    instance_type = ContentType.objects.get_for_model(instance.__class__)

    return ModelInstanceRef(instance_type.pk, instance.pk)

def get_ref_for_queryset(queryset):
    queryset_type = ContentType.objects.get_for_model(queryset.model)

    return ModelQuerySetRef(queryset_type.pk, queryset.query)

def get_key_for_instane(fragment_name, template_name, user, instance_ref):
    instance_type_pk = instance_ref.instance_type_pk
    instance_pk = instance_ref.instance_pk

    instance_hash = hashlib.sha1('%d:%d' % (instance_type_pk, instance_pk)).hexdigest()
    fragment_hash = hashlib.sha1('%s:%s' % (fragment_name, template_name)).hexdigest()
    cache_key = 'i%s-f%s' % (instance_hash, fragment_hash)

    if user:
        username_hash = hashlib.sha1('%d:%s' % (user.id, user.username)).hexdigest()
        cache_key = '%s-u%s' % (cache_key, username_hash)

    return cache_key

def get_key_for_queryset(fragment_name, template_name, user, queryset_ref):
    queryset_type_pk = queryset_ref.queryset_type_pk
    queryset_dump = hashlib.sha1(str(queryset_ref.query)).hexdigest()

    queryset_hash = hashlib.sha1('%d:qs' % queryset_type_pk).hexdigest()
    fragment_hash = hashlib.sha1('%s:%s' % (fragment_name, template_name)).hexdigest()
    cache_key = 'q%s-d%s-f%s' % (queryset_hash, queryset_dump, fragment_hash)

    if user:
        username_hash = hashlib.sha1('%d:%s' % (user.id, user.username)).hexdigest()
        cache_key = '%s-u%s' % (cache_key, username_hash)

    return cache_key

def listen_on_instance(channel_cache, cache_key, template_name, new_context, instance_ref):
    tmpl_cache_key = 'sdl.tmpl.%s' % cache_key
    refc_cache_key = 'sdl.refc.%s' % cache_key

    channel_cache.set(tmpl_cache_key, (template_name, new_context))
    channel_cache.add(refc_cache_key, 0)

def listen_on_queryset(channel_cache, cache_key, template_name, new_context, queryset_ref):
    tmpl_cache_key = 'sdl.tmpl.%s' % cache_key
    data_cache_key = 'sdl.data.%s' % cache_key
    refc_cache_key = 'sdl.refc.%s' % cache_key

    channel_cache.set(data_cache_key, (template_name, new_context))
    channel_cache.set(tmpl_cache_key, (queryset_ref, data_cache_key))
    channel_cache.add(refc_cache_key, 0)

@register.simple_tag(takes_context=True)
def include_live(context, fragment_name, template_name, **kwargs):
    if 'user' in context:
        user = context['user']
        kwargs['user'] = user
    else:
        user = None

    new_context_data = {}
    for key, value in kwargs.items():
        if isinstance(value, Model):
            new_context_data[key] = get_ref_for_instance(instance=value)
        elif isinstance(value, QuerySet):
            new_context_data[key] = get_ref_for_queryset(queryset=value)
        else:
            new_context_data[key] = value

    cache_keys = {}
    for value in new_context_data.values():
        if isinstance(value, ModelInstanceRef):
            cache_key = get_key_for_instane(fragment_name, template_name,
                                            user, instance_ref=value)
            cache_keys[cache_key] = value
        elif isinstance(value, ModelQuerySetRef):
            cache_key = get_key_for_queryset(fragment_name, template_name,
                                             user, queryset_ref=value)
            cache_keys[cache_key] = value

    make_channel = lambda c: 'swampdragon-live-%s' % c
    channels = map(make_channel, cache_keys.keys())
    classes = 'swampdragon-live %s' % ' '.join(channels)

    new_context_data['swampdragon_live'] = classes
    new_context_data['is_swampdragon_live'] = False
    new_context = ContextRef(new_context_data)

    channel_cache = get_channel_cache()
    for cache_key, value in cache_keys.items():
        if isinstance(value, ModelInstanceRef):
            listen_on_instance(channel_cache, cache_key, template_name,
                               new_context, instance_ref=value)
        elif isinstance(value, ModelQuerySetRef):
            listen_on_queryset(channel_cache, cache_key, template_name,
                               new_context, queryset_ref=value)

    return get_template(template_name).render(new_context)
