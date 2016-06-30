from django.contrib.auth.decorators import permission_required, login_required
from django.conf.urls import url


def permission_required_url(permission, regex, view, *args, **kwargs):
    return url(regex,
               permission_required(permission, raise_exception=True)(view),
               *args, **kwargs)

def login_required_url(regex, view, *args, **kwargs):
    return url(regex, login_required(view), *args, **kwargs)
