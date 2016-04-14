# -*- coding: utf-8 -*-
from django.db.models.signals import post_save, pre_delete, post_delete
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
import hashlib

from .utils import get_channel_cache
from .pushers import push_new_content_for_instance
from .pushers import push_new_content_for_queryset

@receiver(post_save)
def post_save_handler(sender, instance, created, **kwargs):
    if ContentType.objects.exists():
        instance_type = ContentType.objects.get_for_model(instance.__class__)
        channel_cache = get_channel_cache()

        if created:
            queryset_hash = hashlib.sha1('%d:qs' % instance_type.pk).hexdigest()
            pushers = push_new_content_for_queryset(channel_cache, queryset_hash, instance.pk)
        else:
            instance_hash = hashlib.sha1('%d:%d' % (instance_type.pk, instance.pk)).hexdigest()
            pushers = push_new_content_for_instance(channel_cache, instance_hash, instance.pk)

        for pusher in pushers:
            pusher()

@receiver(pre_delete)
def pre_delete_handler(sender, instance, **kwargs):
    if ContentType.objects.exists():
        instance_type = ContentType.objects.get_for_model(instance.__class__)
        channel_cache = get_channel_cache()

        queryset_hash = hashlib.sha1('%d:qs' % instance_type.pk).hexdigest()
        pushers = push_new_content_for_queryset(channel_cache, queryset_hash, instance.pk)
        instance.__swampdragon_live_pushers__ = list(pushers)

@receiver(post_delete)
def post_delete_handler(sender, instance, **kwargs):
    if hasattr(instance, '__swampdragon_live_pushers__'):
        for pusher in instance.__swampdragon_live_pushers__:
            pusher()
