# -*- coding: UTF-8 -*-
"""
    Created by Régis Eduardo Crestani <regis.crestani@gmail.com> on 02/07/2016.
"""
from django.conf import settings

DJANGO_USAGE_SETTINGS = getattr(settings, "DJANGO_USAGE_SETTINGS", {})

"""
    PARALLEL MODE:
        0: No parallel
        1: Thread
        2: Process
"""
DJANGO_USAGE_SETTINGS.setdefault("PARALLEL_MODE", 1)

DJANGO_USAGE_SETTINGS.setdefault("DATABASE", 'default')
