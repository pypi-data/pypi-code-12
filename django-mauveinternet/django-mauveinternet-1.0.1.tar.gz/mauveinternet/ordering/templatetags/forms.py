from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings
from django.utils.safestring import mark_safe

register=Library()

@register.inclusion_tag('form_field.html')
def formfield(field):
    return {'field':field}
