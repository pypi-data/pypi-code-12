import functools

from django.conf import settings
from django.shortcuts import redirect


def authenticated_redirect(view_func=None, path=None):
    """
    Decorator for an already authenticated user that we don't want to serve a
    view to. Instead we send them to the dashboard by default or a specified
    path.

    Usage:

        @authenticated_redirect
        @authenticated_redirect()
        @authenticated_redirect(path='home')

    """

    default_path = getattr(settings, 'DEFAULT_AUTHENTICATED_PATH', 'dashboard')

    if view_func is None:
        return functools.partial(authenticated_redirect, path=path)

    @functools.wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if path == request.path.replace('/', ''):
            return redirect(default_path)

        if request.user.is_authenticated():
            return redirect(path or default_path)

        return view_func(request, *args, **kwargs)
    return _wrapped_view
