from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render


def home(request):
    """Mock home view"""
    return HttpResponse('home')


def login(request):
    """Mock login view"""
    return HttpResponse('login')


def dashboard(request):
    """Mock dashboard view"""
    return HttpResponse('dashboard')

urlpatterns = [
    url(r'^', home, name='home'),
    url(r'^login/$', login, name='login'),
    url(r'^dashboard/$', dashboard, name='dashboard'),
]
