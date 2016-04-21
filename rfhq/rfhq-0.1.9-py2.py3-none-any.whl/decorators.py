# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function
from rest_framework.parsers import BaseParser


class SkipParser(BaseParser):

    media_type = '*/*'

    def parse(self, stream, media_type=None, parser_context=None):
        return


def detail_route_view(methods=None, **kwargs):
    """
    Used to mark a method on a ViewSet that should be routed to a different view for detail requests.

    The decorator must ensure that the ViewSet's permissions, parsers, method restrictions, etc. are ignored
    """
    view_kwargs = kwargs
    fake_kwargs = {'permission_classes': (), 'parser_classes': (SkipParser,), 'url_path': view_kwargs.pop('url_path', None), 'throttle_classes': []}
    methods = ['get', 'post', 'put', 'patch', 'options', 'head', 'delete'] if (methods is None) else methods

    def decorator(func=None):
        def deferred_view(self, request, *args, **kwargs):
            if not hasattr(func, 'view'):
                # instantiate view once only
                func.view = func(self).as_view(**view_kwargs)
            return func.view(request._request, *args, **kwargs)
        deferred_view.bind_to_methods = methods
        deferred_view.detail = True
        deferred_view.kwargs = fake_kwargs
        return deferred_view
    return decorator
