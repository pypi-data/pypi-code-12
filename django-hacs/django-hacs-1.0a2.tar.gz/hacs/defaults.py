# -*- coding: utf-8 -*-
# ++ This file `defaults.py` is generated at 3/3/16 6:15 AM ++
from django.apps import apps
from django.conf import settings
from django.utils._os import safe_join

from .globals import HACS_APP_NAME
__author__ = "Md Nazrul Islam<connect2nazrul@gmail.com>"

HACS_CACHE_SETTING_NAME = 'default'
HACS_FALLBACK_URLCONF = settings.ROOT_URLCONF
HACS_GENERATED_URLCONF_DIR = safe_join(apps.get_app_config(HACS_APP_NAME).path, 'generated')
HACS_SERIALIZED_ROUTING_DIR = None
HACS_USER_OBJECT_QUERY_CALLABLE = "hacs.utils.get_user_object"
