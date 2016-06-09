# coding: utf-8
from django.conf.urls import patterns
from django.conf import settings
from creadoc.controller import creadoc_controller
from creadoc.designer.actions import CreadocDesignerActionPack
from creadoc.report.actions import CreadocDataSourceActionPack
from creadoc.viewer.actions import CreadocViewerActionPack

__author__ = 'damirazo <me@damirazo.ru>'


def register_actions():
    creadoc_controller.extend_packs([
        CreadocDesignerActionPack(),
        CreadocViewerActionPack(),
        CreadocDataSourceActionPack(),
    ])


def register_urlpatterns():
    return patterns('', (
        '^{}'.format(settings.CREADOC_URL),
        creadoc_controller.process_request
    ))
