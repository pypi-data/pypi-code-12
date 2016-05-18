"""Views for the eckerd-django-google-sso app."""
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('http://its.eckerd.edu')


def context(**extra):
    return dict(**extra)


def login(request):
    return redirect('/login/google-oauth2/')
