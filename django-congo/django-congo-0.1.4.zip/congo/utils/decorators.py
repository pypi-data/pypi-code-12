# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse

def secure_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrapped_view.secure = True
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

def secure_allowed(view_func):
    def wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    wrapped_view.secure = None
    wrapped_view.__name__ = view_func.__name__
    return wrapped_view

def staff_required(view_func):
    decorator = user_passes_test(lambda u: u.is_staff)
    return decorator(view_func)

def superuser_required(view_func):
    decorator = user_passes_test(lambda u: u.is_superuser)
    return decorator(view_func)

def active_required(view_func):
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.is_active:
                return view_func(request, *args, **kwargs)
            else:
                message = _("Your account is inactive. To use all the features of the service, click the link in the message you received during registration or contact Customer Service.")
                messages.warning(request, message)
                return HttpResponseRedirect(reverse('accounts_account'))
        else:
            return redirect_to_login(request.build_absolute_uri())
    return wrapped_view
