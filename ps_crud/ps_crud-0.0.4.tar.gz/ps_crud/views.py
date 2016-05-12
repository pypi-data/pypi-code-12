#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

"""
Custom gettext for ps_crud
"""
from pyramid.events import BeforeRender, NewRequest, subscriber
from pyramid.i18n import get_localizer

from .localization import _ps_crud


@subscriber(BeforeRender)
def add_renderer_globals(event):
    request = event['request']
    event['_ps_crud'] = request.ps_crud_translate


@subscriber(NewRequest)
def add_localizer(event):
    request = event.request
    localizer = get_localizer(request)

    def auto_translate(string):
        return localizer.translate(_ps_crud(string))
    request.localizer = localizer
    request.ps_crud_translate = auto_translate
