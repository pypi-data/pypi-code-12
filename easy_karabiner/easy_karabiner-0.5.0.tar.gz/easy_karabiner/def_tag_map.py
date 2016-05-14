# -*- coding: utf-8 -*-
from __future__ import print_function
from . import util
from . import config


def _get_def_tag_maps():
    if not hasattr(_get_def_tag_maps, 'maps'):
        maps = util.read_python_file(config.get_data_path('def_tag_map.data'))['DEF_TAG_MAP']
        _get_def_tag_maps.maps = maps
    return _get_def_tag_maps.maps


def _get(def_tag):
    return _get_def_tag_maps().get(def_tag, [None, None])


def get_name_tag_name(def_tag):
    return _get(def_tag)[0]


def get_filter_class_name(def_tag):
    return _get(def_tag)[1]
