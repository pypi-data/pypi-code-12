# coding: utf-8
from django.conf.urls import patterns
from django.conf import settings
from creadoc.controller import creadoc_controller

__author__ = 'damirazo <me@damirazo.ru>'


def register_urlpatterns():
    return patterns('', (
        '^{}'.format(settings.CREADOC_URL),
        creadoc_controller.process_request
    ))
