# -*- coding: UTF-8 -*-
"""
    Created by Régis Eduardo Crestani <regis.crestani@gmail.com> on 02/07/2016.
"""
from django.conf import settings

DJANGO_REST_SCAFFOLD_SETTINGS = getattr(settings, "DJANGO_REST_SCAFFOLD_SETTINGS", {})

DJANGO_REST_SCAFFOLD_SETTINGS.setdefault("APPS_FOLDER", settings.BASE_DIR)
DJANGO_REST_SCAFFOLD_SETTINGS.setdefault("APPS_FOLDER_NAME", None)
