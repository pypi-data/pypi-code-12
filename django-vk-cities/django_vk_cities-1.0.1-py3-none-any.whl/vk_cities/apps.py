# coding=utf-8

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ModuleConfig(AppConfig):

    """Module configuration."""

    name = 'vk_cities'
    verbose_name = _('VK cities')
