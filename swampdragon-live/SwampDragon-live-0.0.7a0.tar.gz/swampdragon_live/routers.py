# -*- coding: utf-8 -*-
from swampdragon import route_handler
from swampdragon.route_handler import BaseRouter
import hashlib

from .utils import get_channel_cache

class LiveTemplateRouter(BaseRouter):
    route_name = 'swampdragon-live'
    valid_verbs = ['subscribe', 'unsubscribe']

    def __init__(self, *args, **kwargs):
        self.channel_cache = get_channel_cache()
        return super(LiveTemplateRouter, self).__init__(*args, **kwargs)

    def get_subscription_channels(self, valid_channel=None, **kwargs):
        if valid_channel:
            tmpl_cache_key = valid_channel.replace('swampdragon-live-', 'sdl.tmpl.')
            if self.channel_cache.get(tmpl_cache_key):
                return [valid_channel]
        return []

    def subscribe(self, **kwargs):
        channel = kwargs.get('channel')
        if channel and self.validate_channel(channel):
            self.subscribe_valid_channel(channel)
            kwargs['valid_channel'] = channel
        elif 'valid_channel' in kwargs:
            del kwargs['valid_channel']
        return super(LiveTemplateRouter, self).subscribe(**kwargs)

    def unsubscribe(self, **kwargs):
        channel = kwargs.get('channel')
        if channel and self.validate_channel(channel):
            self.unsubscribe_valid_channel(channel)
            kwargs['valid_channel'] = channel
        elif 'valid_channel' in kwargs:
            del kwargs['valid_channel']
        return super(LiveTemplateRouter, self).unsubscribe(**kwargs)

    def validate_channel(self, channel):
        if channel.startswith('swampdragon-live-'):
            channel_last_part = channel.split('-')[-1]
            if channel_last_part.startswith('u'):
                user = self.connection.get_user()
                if user:
                    username_hash = hashlib.sha1('%d:%s' % (user.id, user.username)).hexdigest()
                    if username_hash and channel_last_part[1:] == username_hash:
                        return True
            elif channel_last_part.startswith('f'):
                return True
        return False

    def subscribe_valid_channel(self, channel):
        cache_key = '-'.join(channel.split('-')[2:])
        tmpl_cache_key = 'sdl.tmpl.%s' % cache_key
        data_cache_key = 'sdl.data.%s' % cache_key
        refc_cache_key = 'sdl.refc.%s' % cache_key
        if self.channel_cache.incr(refc_cache_key):
            self.channel_cache.expire(tmpl_cache_key, timeout=300)
            self.channel_cache.expire(data_cache_key, timeout=300)
            self.channel_cache.expire(refc_cache_key, timeout=300)

    def unsubscribe_valid_channel(self, channel):
        cache_key = '-'.join(channel.split('-')[2:])
        tmpl_cache_key = 'sdl.tmpl.%s' % cache_key
        data_cache_key = 'sdl.data.%s' % cache_key
        refc_cache_key = 'sdl.refc.%s' % cache_key
        if not self.channel_cache.decr(refc_cache_key):
            self.channel_cache.delete(tmpl_cache_key)
            self.channel_cache.delete(data_cache_key)
            self.channel_cache.delete(refc_cache_key)

route_handler.register(LiveTemplateRouter)
