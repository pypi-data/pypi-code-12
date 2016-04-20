# -*- coding: utf-8 -*-
from django.conf import settings
from appconf import AppConf


class GeopositionConf(AppConf):
    MAP_WIDGET_HEIGHT = 550
    MAP_OPTIONS = {}
    MARKER_OPTIONS = {}

    class Meta:
        prefix = 'geoposition'
