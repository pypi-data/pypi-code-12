# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

from rest_framework.views import get_view_name as get_default_view_name


def get_view_name(view_cls, suffix=None):
    if hasattr(view_cls, 'view_name'):
        return view_cls.view_name
    return get_default_view_name(view_cls, suffix)
