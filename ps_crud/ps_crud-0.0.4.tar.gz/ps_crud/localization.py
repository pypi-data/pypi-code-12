#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 uralbash <root@uralbash.ru>
#
# Distributed under terms of the MIT license.

from pyramid.i18n import TranslationStringFactory

_ps_crud = TranslationStringFactory('ps_crud')


def includeme(config):
    config.add_translation_dirs('ps_crud:locale/')
    config.scan('.views')
