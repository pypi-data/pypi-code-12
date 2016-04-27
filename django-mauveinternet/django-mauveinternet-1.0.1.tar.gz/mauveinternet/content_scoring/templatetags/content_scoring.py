from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings
from django.utils.safestring import mark_safe

from findaholidaylet.properties.content_scoring import content_score

register = Library()
register.filter(content_score)

@register.filter
def content_score_check(text, arg):
    threshold = float(arg)
    return content_score(text) > threshold
