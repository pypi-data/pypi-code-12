#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.contrib import admin

from ishtar_common.admin import HistorizedObjectAdmin, GeneralTypeAdmin

import models


class DatingAdmin(admin.ModelAdmin):
    list_display = ('period', 'start_date', 'end_date', 'dating_type',
                    'quality')
    list_filter = ("period", 'dating_type', 'quality')
    model = models.Dating

admin.site.register(models.Dating, DatingAdmin)


class ContextRecordAdmin(HistorizedObjectAdmin):
    list_display = ('label', 'length', 'width',
                    'thickness', 'depth')
    list_filter = ('has_furniture',)
    search_fields = ('parcel__operation__name', "datings__period__label")
    model = models.ContextRecord

admin.site.register(models.ContextRecord, ContextRecordAdmin)


class ContextRecordSourceAdmin(admin.ModelAdmin):
    list_display = ('context_record', 'title', 'source_type',)
    list_filter = ('source_type',)
    search_fields = ('title', )
    model = models.ContextRecordSource

admin.site.register(models.ContextRecordSource, ContextRecordSourceAdmin)


class RecordRelationsAdmin(admin.ModelAdmin):
    list_display = ('left_record', 'relation_type', 'right_record')
    list_filter = ('relation_type',)

admin.site.register(models.RecordRelations, RecordRelationsAdmin)


class RelationTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'txt_idx', 'available', 'symmetrical',
                    'inverse_relation')

admin.site.register(models.RelationType, RelationTypeAdmin)

general_models = [models.DatingType, models.DatingQuality,
                  models.Unit, models.ActivityType, models.IdentificationType]
for model in general_models:
    admin.site.register(model, GeneralTypeAdmin)
