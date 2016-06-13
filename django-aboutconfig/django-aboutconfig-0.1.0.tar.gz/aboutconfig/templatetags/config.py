from django import template
from django.template.defaultfilters import stringfilter

from .. import utils

# pylint: disable=invalid-name
register = template.Library()


@register.filter
@stringfilter
def get_config(key, default=None):
    data = utils.get_config(key, value_only=False)

    if data.allow_template_use:
        return default if data.value is None else data.value
    else:
        return default
