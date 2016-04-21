#coding=utf-8
from django import template
from django.conf import settings as django_settings

register = template.Library()


@register.simple_tag
def settings(name):
    return getattr(django_settings, name, "")


@register.assignment_tag
def settings_value(name):
    return getattr(django_settings, name, "")