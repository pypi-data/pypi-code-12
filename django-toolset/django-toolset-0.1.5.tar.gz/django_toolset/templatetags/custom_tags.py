import re

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def active(context, pattern_or_urlname, class_name='active', *args, **kwargs):
    """Based on a URL Pattern or name, determine if it is the current page.

    This is useful if you're creating a navigation component and want to give
    the active URL a specific class for UI purposes. It will accept a named
    URL or a regex pattern. If you have a URL which accepts args or kwargs then
    you may pass them into the tag and they will be picked up for matching as
    well.

    Usage:

        {% load custom_tags %}

        <li class="nav-home {% active 'url-name' %}">
            <a href="#">Home</a>
        </li>

        OR

        <li class="nav-home {% active '^/regex/' %}">
            <a href="#">Home</a>
        </li>

        OR

        <li class="nav-home {% active 'url-name' class_name='current' %}">
            <a href="#">Home</a>
        </li>

        OR

        <li class="nav-home {% active 'url-name' username=user.username %}">
            <a href="#">Home</a>
        </li>

    """
    request = context.dicts[1].get('request')

    try:
        pattern = '^%s$' % reverse(pattern_or_urlname, args=args,
                                   kwargs=kwargs)
    except NoReverseMatch:
        pattern = pattern_or_urlname

    if request and re.search(pattern, request.path):
        return class_name

    return ''

