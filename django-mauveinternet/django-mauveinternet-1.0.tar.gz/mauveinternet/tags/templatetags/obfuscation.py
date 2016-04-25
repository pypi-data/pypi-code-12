from cStringIO import StringIO

from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.filter
def obfuscate_email(email):
    s = StringIO()
    for c in email:
        s.write('&#%d;' % ord(c))
    return mark_safe(s.getvalue())


@register.filter
def split_email(email):
    replacements = {
            '.': 'dot',
            '@': 'at',
            '_': 'underscore',
            '-': 'hyphen'
    }
    for char, repl in replacements.items():
        s = s.replace(char, u' %s ' % repl)
    return s
