from django.template import Node, Library, resolve_variable, TemplateSyntaxError
from django.conf import settings
from django.utils.safestring import mark_safe

register = Library()

@register.filter(name='gridify')
def gridify(lst, cols=3):
    out = []
    while True:
        head, lst = lst[:cols], lst[cols:]
        if len(head) < cols:
            out.append([i for i in head] + (cols - len(head)) * [None])
            break
        out.append(head)

    return out
