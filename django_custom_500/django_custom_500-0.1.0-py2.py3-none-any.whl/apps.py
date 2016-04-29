# !/usr/bin/python
# coding=utf-8

from __future__ import (absolute_import, division, print_function, unicode_literals)

try:
    from django.apps import AppConfig
except ImportError:
    AppConfig = object


class DjangoCustom500AppConfig(AppConfig):
    """
    Django app config, this will set human readable name in Django admin.
    """

    name = 'django_custom_500'
    verbose_name = "Django custom 500"

    def ready(self):
        pass
