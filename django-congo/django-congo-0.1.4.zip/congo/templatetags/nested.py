# -*- coding: utf-8 -*-
from congo.templatetags import Library
from congo.templatetags import common
register = Library()

@register.smart_tag
def google_maps(mode, **kwargs):
    return common.google_maps(mode, **kwargs)
