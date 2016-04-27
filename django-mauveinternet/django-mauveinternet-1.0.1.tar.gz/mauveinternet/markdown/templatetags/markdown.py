from __future__ import absolute_import
from django.apps import apps
from django.conf import settings
from django import template
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe

from .. import _link_providers

register = template.Library()


def lookup_link(internal_link):
    import re
    mo = re.match(r'internal:(?P<app_label>\w+)\.(?P<model_name>\w+)/(?P<pk>\d+)/?', internal_link)
    if not mo:
        raise ValueError(u'Malformed internal link')
    model = apps.get_model(mo.group('app_label'), mo.group('model_name'))
    if model not in _link_providers:
        raise ValueError(u'Linking to %s is not permitted' % unicode(model._meta.verbose_name_plural))
    inst = model._default_manager.get(pk=mo.group('pk'))
    return inst.get_absolute_url()


@register.filter
def markdown(value, arg=''):
    """
    This version of the Markdown template filter is based on the version
    that is supplied with Django, but expands encoded internal links to
    the correct URLs.

    Another difference is that this version drops the heading level by two levels,
    which is useful  where <h1> is site title and <h2> is page title.

    Unlike Django's version of this function, we skip import/compatibility because
    a compatible version is bundled (this is at least Markdown 1.7, as
    earlier versions have bugs with Unicode support).
    """
    import re
    import markdown

    extensions = set([e for e in arg.split(",") if e])
    if 'safe' in extensions:
        extensions.remove('safe')
        safe_mode = True
    else:
        safe_mode = False

    min_h = 3
    if 'minh=2' in extensions:
        min_h = 2
    if 'minh=1' in extensions:
        min_h = 1
    html = markdown.markdown(force_unicode(value), safe_mode=safe_mode)
    if min_h > 1:
        html = re.sub(r'<(/?)h([1-6])(\s.*?)?>', lambda mo: '<%sh%d%s>' % (mo.group(1), min(6, int(mo.group(2)) + min_h - 1), mo.group(3) or ''), html)
    html = re.sub(r'(<a\s+[^>]*)href="(internal:.*?)"', lambda mo: '%shref="%s"' % (mo.group(1), lookup_link(mo.group(2))), html)
    return mark_safe(html)
markdown.is_safe = True
