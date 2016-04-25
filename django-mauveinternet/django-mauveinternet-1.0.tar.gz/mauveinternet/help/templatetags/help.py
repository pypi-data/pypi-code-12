import re

from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings
from django.utils.safestring import mark_safe

from django.core.urlresolvers import reverse

from mauveinternet.help.models import *

register = Library()

class InlineHelpNode(Node):
    """Checks the database for an inline help object corresponding to the slug
    specified in the template.

    If there is a non-empty help for the node, return a link for it."""

    def __init__(self, slug):
        self.slug = slug

    def render(self, context):
        return self.get_help(self.slug)

    def get_help(self, slug):
        help, created = InlineHelp.objects.get_or_create(slug=slug)
        if created or not help.description:
            return ''

        return mark_safe(' <a class="inlinehelp" href="%s" target="inlinehelp" title="Help on this item"><img src="/assets/images/help_icon.png" alt="?" /></a>' % reverse('quick-help', kwargs={'slug': slug}))


class FormHelpNode(InlineHelpNode):
    """Does the same thing as InlineHelpNode but constructs a slug for a form
    field based on the form class and the field name"""

    def __init__(self, formfield_variable):
        self.formfield_variable = formfield_variable

    def render(self, context):
        field = resolve_variable(self.formfield_variable, context)
        slug = '%s-%s' % (field.form.__class__.__name__.lower(), field.name.lower())
        slug = re.sub(r'\d+', '', slug)
        return self.get_help(slug)


def parse_help_node(parser, token):
    try:
        name, slug = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one argument" % name

    return InlineHelpNode(slug)


def parse_formhelp_node(parser, token):
    try:
        name, formfield = token.split_contents()
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one argument" % name

    return FormHelpNode(formfield)


register.tag('help', parse_help_node)
register.tag('formhelp', parse_formhelp_node)
