# -*- coding: utf-8 -*-
from django.conf import settings
from django import template
#from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext_lazy as _

register = template.Library()

@register.filter
@stringfilter
def get_kind_display(value):
    """
    Return Entity kind display name from its given key name
    
    Also enforce i18n usage on choices labels
    """
    return _(dict(settings.ENTITY_KINDS).get(value))
