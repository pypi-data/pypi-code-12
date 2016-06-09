#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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


class AdministrativeActAdmin(HistorizedObjectAdmin):
    list_display = ('year', 'index', 'operation', 'associated_file',
                    'act_type')
    list_filter = ('act_type',)
    search_fields = ('year', 'index')
    readonly_fields = ('in_charge', 'operator', 'scientist', 'signatory',
                       'associated_file', 'imports',
                       'departments_label', 'towns_label',
                       'history_modifier', 'history_creator')
    model = models.AdministrativeAct

admin.site.register(models.AdministrativeAct, AdministrativeActAdmin)


class PeriodAdmin(admin.ModelAdmin):
    list_display = ('label', 'start_date', 'end_date', 'parent', 'available',
                    'order')
    list_filter = ('parent',)
    model = models.Period

admin.site.register(models.Period, PeriodAdmin)


class ArchaeologicalSiteAdmin(HistorizedObjectAdmin):
    list_display = ('name', 'reference')
    search_fields = ('name', 'reference')
    model = models.ArchaeologicalSite

admin.site.register(models.ArchaeologicalSite, ArchaeologicalSiteAdmin)


class OperationAdmin(HistorizedObjectAdmin):
    list_display = ['year', 'operation_code', 'start_date',
                    'excavation_end_date', 'end_date',
                    'operation_type']
    list_filter = ("year", "operation_type",)
    search_fields = ['towns__name', 'operation_code']
    if settings.COUNTRY == 'fr':
        list_display += ['code_patriarche']
        search_fields += ['code_patriarche']
    model = models.Operation

admin.site.register(models.Operation, OperationAdmin)


class OperationSourceAdmin(admin.ModelAdmin):
    list_display = ('operation', 'title', 'source_type',)
    list_filter = ('source_type',)
    search_fields = ('title', 'operation__common_name')
    model = models.OperationSource

admin.site.register(models.OperationSource, OperationSourceAdmin)


class ParcelAdmin(HistorizedObjectAdmin):
    list_display = ['section', 'parcel_number', 'operation', 'associated_file']
    search_fields = ('operation__name',)
    model = models.Parcel

admin.site.register(models.Parcel, ParcelAdmin)


class RecordRelationsAdmin(admin.ModelAdmin):
    list_display = ('left_record', 'relation_type', 'right_record')
    list_filter = ('relation_type',)

admin.site.register(models.RecordRelations, RecordRelationsAdmin)


class RelationTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'txt_idx', 'available', 'symmetrical',
                    'inverse_relation')

admin.site.register(models.RelationType, RelationTypeAdmin)

general_models = [models.RemainType, models.ActType, models.ReportState]
for model in general_models:
    admin.site.register(model, GeneralTypeAdmin)

basic_models = [models.ParcelOwner]
for model in basic_models:
    admin.site.register(model)
