#!/usr/bin/python

from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings

from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape

from django.core.urlresolvers import reverse

register=Library()

class ItemViewNode(Node):
    """Implements an input field for updating basket values."""

    def __init__(self, url_name, item, args):
        self.url_name=url_name
        self.item=item
        self.args=args

    def render(self, context):
        orderitem=resolve_variable(self.item, context)
        rargs=[resolve_variable(a, context) for a in self.args]
        if hasattr(orderitem, 'item_view'):
            return mark_safe(u'<a href="%s?item=%d">%s</a>'%(reverse(self.url_name, args=rargs), orderitem.list_id, conditional_escape(unicode(orderitem))))
        return conditional_escape(unicode(orderitem))

def parse_item_view_node(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        url = token.split_contents()[1]
        item = token.split_contents()[2]
        args = token.split_contents()[3:]
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one arguments" % name

    return ItemViewNode(url, item, args)

register.tag('item_view', parse_item_view_node)
