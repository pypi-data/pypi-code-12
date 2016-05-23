# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import HeaderControlPluginModel


class HeaderControlPlugin(CMSPluginBase):
    allow_children = True
    cache = True
    model = HeaderControlPluginModel
    name = _('Header control')
    render_template = 'header_control/plugin.html'
    filter_horizontal = ('headers', )

    def get_cache_expiration(self, request, instance, placeholder):
        return instance.cache_duration

    def get_vary_cache_on(self, request, instance, placeholder):
        return instance.headers.values_list('header_name', flat=True)

    def render(self, context, instance, placeholder):
        return super(HeaderControlPlugin, self).render(context, instance, placeholder)


plugin_pool.register_plugin(HeaderControlPlugin)
