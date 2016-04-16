from functools import wraps

from cached_httpbl.middleware import CachedHTTPBLViewMiddleware
from django.utils.decorators import available_attrs, decorator_from_middleware


cached_httpbl_protect = decorator_from_middleware(CachedHTTPBLViewMiddleware)
cached_httpbl_protect.__name__ = "cached_httpbl_protect"
cached_httpbl_protect.__doc__ = """
This decorator adds cached httpbl protection in exactly the same way as
CachedHTTPBLViewMiddleware, but it can be used on a per view basis.  Using both, or
using the decorator multiple times, is harmless and efficient.
"""


def cached_httpbl_exempt(view_func):
    """
    Marks a view function as being exempt from the cached httpbl view protection.
    """
    # We could just do view_func.cached_httpbl_exempt = True, but decorators
    # are nicer if they don't have side-effects, so we return a new
    # function.
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    wrapped_view.cached_httpbl_exempt = True
    return wraps(view_func, assigned=available_attrs(view_func))(wrapped_view)
