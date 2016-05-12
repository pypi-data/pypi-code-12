#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.


def includeme(config):
    config.include('.localization')
    config.include('pyramid_jinja2')
    config.add_jinja2_search_path("templates")
    config.add_static_view('ps_crud_static', 'ps_crud:static')
