#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
from django.contrib import admin

from ishtar_common.admin import HistorizedObjectAdmin, GeneralTypeAdmin

import models


class FileAdmin(HistorizedObjectAdmin):
    list_display = ['year', 'numeric_reference', 'internal_reference',
                    'end_date', 'file_type', 'general_contractor']
    if settings.COUNTRY == 'fr':
        list_display += ['saisine_type', 'permit_reference']
    list_filter = ("file_type", "year",)
    search_fields = ('towns__name',)
    model = models.File

admin.site.register(models.File, FileAdmin)

general_models = [models.FileType, models.PermitType]
if settings.COUNTRY == 'fr':
    general_models.append(models.SaisineType)
for model in general_models:
    admin.site.register(model, GeneralTypeAdmin)
