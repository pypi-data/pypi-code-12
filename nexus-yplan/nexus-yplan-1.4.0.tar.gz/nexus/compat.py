import django

# Django 1.8

# context_processors moved
try:
    from django.template import context_processors  # noqa pragma: no cover
except ImportError:
    from django.core import context_processors  # noqa pragma: no cover


# 'dictionary' -> 'context'
if django.VERSION[:2] >= (1, 8):
    from django.shortcuts import render  # pragma: no cover
    from django.template.loader import render_to_string  # pragma: no cover
else:
    from django.shortcuts import render as orig_render
    from django.template import RequestContext
    from django.template.loader import render_to_string as orig_render_to_string

    def render(*args, **kwargs):
        if 'context' in kwargs:
            kwargs['dictionary'] = kwargs.pop('context')
        return orig_render(*args, **kwargs)

    def render_to_string(*args, **kwargs):
        if 'context' in kwargs:
            kwargs['dictionary'] = kwargs.pop('context')
        request = kwargs.pop('request', None)
        if request is not None:
            kwargs['context_instance'] = RequestContext()
        return orig_render_to_string(*args, **kwargs)

# Django 1.9

# url(prefix, include(urls, namespace, name)) -> url(prefix, (urls, namespace, name))
if django.VERSION[:2] >= (1, 9):
    def subinclude(urls_tuple):
        return urls_tuple  # (urls, namespace, name)
else:
    from django.conf.urls import include as subinclude  # noqa
