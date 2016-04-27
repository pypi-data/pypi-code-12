from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings
from django.utils.safestring import mark_safe

from django.contrib.sites.models import Site

from django.template import defaulttags

register = Library()

class AbsoluteURLNode(defaulttags.URLNode):
    """Template tag similar to Django's built-in URL tag, but qualifying the relative
    URL by prefixing it with the current Site domain, to build an absolute link."""
    def render(self, context):
        url = super(AbsoluteURLNode, self).render(context)
        base_url = 'http://' + Site.objects.get_current().domain

        if self.asvar:
            context[self.asvar] = base_url + context[self.asvar]
            return url
        else:
            return base_url + url


@register.tag(name="absolute-url")
def absolute_url(parser, token):
    node = defaulttags.url(parser, token)
    return AbsoluteURLNode(node.view_name, node.args, node.kwargs, node.asvar)


@register.filter
def absolutize(url, scheme='http'):
    return scheme + '://' + Site.objects.get_current().domain + url
