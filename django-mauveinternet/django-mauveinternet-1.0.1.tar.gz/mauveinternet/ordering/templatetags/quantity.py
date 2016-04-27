#!/usr/bin/python

from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings
from django.utils.safestring import mark_safe

register=Library()

class QuantityNode(Node):
    """Implements an input field for updating basket values."""

    def __init__(self, value):
        self.value=value

    def render(self, context):
        orderitem=resolve_variable(self.value, context)
        if hasattr(orderitem, 'set_quantity'):
            return mark_safe(u'<input class="qty" name="%d__qty" value="%d" />'%(orderitem.list_id, orderitem.quantity))
        return orderitem.quantity

def parse_quantity_node(parser, token):
    """Displays an input field for updating basket quantities if the
    item given allows quantity to be changed; otherwise it just displays the
    current quantity.
    """
    try:
        # split_contents() knows not to split quoted strings.
        value = token.split_contents()[1]
    except ValueError:
        raise TemplateSyntaxError, "%r tag requires exactly one arguments" % name

    return QuantityNode(value)

register.tag('quantity', parse_quantity_node)
