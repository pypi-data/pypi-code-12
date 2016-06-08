#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
from django.utils import translation
from django.utils.translation import pgettext_lazy

# [('study', pgettext_lazy('ooo key', u'study')),]
TRANSLATION_STRINGS = []

ooo_translation = {}
cur_language = translation.get_language()

try:
    for language, lbl in settings.LANGUAGES:
        translation.activate(language)
        ooo_translation[language] = {}
        for k, v in TRANSLATION_STRINGS:
            ooo_translation[language][k] = unicode(v)
finally:
    translation.activate(cur_language)
