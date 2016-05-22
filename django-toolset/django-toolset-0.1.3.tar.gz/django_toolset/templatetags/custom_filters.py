from functools import partial

from django import template

register = template.Library()


@register.filter
def method(value, arg):
    """Method attempts to see if the value has a specified method.

    Usage:

        {% load custom_filters %}
        {% if foo|method:"has_access" %}

    """
    if hasattr(value, str(arg)):
        return getattr(value, str(arg))
    return "[%s has no method %s]" % (value, arg)


@register.filter(name="with")
def with_(value, arg):
    """With build up params for a callable returning a new function with the arg.

    Usage:

        {% load custom_filters %}
        {% if foo|method:"has_access"|with:user|with:group|call %}

    This will invoke foo.has_access(user, group)

    """
    if callable(value):
        return partial(value, arg)
    return "[%s is not callable]" % value


@register.filter
def call(value):
    """Call is meant to be used with the Method filter. It attempts to call
    the method specified.

    Usage:

        {% load custom_filters %}
        {% if foo|method:"has_access"|call %}

    This will invoke foo.has_access()

    """
    if not callable(value):
        return "[%s is not callable]" % value
    return value()
