import re

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname, class_name='active'):
    """Based on a URL Pattern or name, determine if it is the current page.

    This is useful if you're creating a navigation component and want to give
    the active URL a specific class for UI purposes. It will accept a named
    URL or a regex pattern.

    Usage:

        {% load custom_tags %}
        <nav><ul>
          <li class="nav-home {% active 'url-name' %}"><a href="#">Home</a></li>
          <li class="nav-blog {% active '^/regex/' %}"><a href="#">Blog</a></li>
        </ul></nav>

    """
    request = context.dicts[1].get('request')

    try:
        pattern = '^%s$' % reverse(pattern_or_urlname)
    except NoReverseMatch:
        pattern = pattern_or_urlname

    if request and re.search(pattern, request.path):
        return class_name

    return ''
