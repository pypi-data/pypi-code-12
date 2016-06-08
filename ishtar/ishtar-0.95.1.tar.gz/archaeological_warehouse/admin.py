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

from django.contrib import admin

from ishtar_common.admin import HistorizedObjectAdmin, GeneralTypeAdmin

import models


class WarehouseAdmin(HistorizedObjectAdmin):
    list_display = ('name', 'warehouse_type', 'town')
    list_filter = ('warehouse_type',)
    search_fields = ('name', 'town')
    model = models.Warehouse

admin.site.register(models.Warehouse, WarehouseAdmin)


class ContainerTypeAdmin(admin.ModelAdmin):
    list_display = ('label', 'reference', 'length', 'width', 'height',
                    'volume')
    model = models.ContainerType

admin.site.register(models.ContainerType, ContainerTypeAdmin)


class ContainerAdmin(admin.ModelAdmin):
    list_display = ('reference', 'location', 'container_type',)
    list_filter = ("container_type",)
    model = models.Container

admin.site.register(models.Container, ContainerAdmin)

general_models = [models.WarehouseType]
for model in general_models:
    admin.site.register(model, GeneralTypeAdmin)
