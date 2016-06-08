#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# See the file COPYING for details.

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import ugettext
from django.template.defaultfilters import slugify


def get_cache(cls, extra_args=[]):
    cache_key = u"{}-{}".format(settings.PROJECT_SLUG, cls.__name__)
    for arg in extra_args:
        if not arg:
            cache_key += '-0'
        else:
            if type(arg) == dict:
                cache_key += '-' + "_".join([unicode(arg[k]) for k in arg])
            elif type(arg) in (list, tuple):
                cache_key += '-' + "_".join([unicode(v) for v in arg])
            else:
                cache_key += '-' + unicode(arg)
    cache_key = slugify(cache_key)
    return cache_key, cache.get(cache_key)


def cached_label_changed(sender, **kwargs):
    if not kwargs.get('instance'):
        return
    instance = kwargs.get('instance')
    lbl = instance._generate_cached_label()
    if lbl != instance.cached_label:
        instance.cached_label = lbl
        instance.save()

SHORTIFY_STR = ugettext(" (...)")


def shortify(lbl, number=20):
    if len(lbl) <= number:
        return lbl
    return lbl[:number - len(SHORTIFY_STR)] + SHORTIFY_STR
