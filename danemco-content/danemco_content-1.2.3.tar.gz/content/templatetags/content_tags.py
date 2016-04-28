from django.template import TemplateSyntaxError
from django import template

from content.models import Section
from django.conf import settings
from six import text_type

register = template.Library()


@register.assignment_tag()
def concat(*args, **kwargs):
    return "".join([text_type(a) for a in args])


@register.simple_tag(takes_context=True)
def snippet(context, section, default=""):
    section = (section or "").strip()
    if section:
        section = Section.objects.get_or_create(name=section)[0]
        request = context.get('request', None)
        if request:
            path = request.path
        else:
            path = "/"

        my_snippet = section.snippets.from_url(path)
        if my_snippet:
            return my_snippet.render(context)
        return default
    else:
        if settings.TEMPLATE_DEBUG:
            raise TemplateSyntaxError("Invalid snippet key")
        return default
