#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

"""
Admin description
"""
import csv

from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify

from django import forms

import models


class ImportGenericForm(forms.Form):
    _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
    csv_file = forms.FileField(
        "CSV file", help_text="Only unicode encoding is managed - convert your"
        " file first")


def gen_import_generic(self, request, queryset):
    form = None

    if 'apply' in request.POST:
        form = ImportGenericForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['csv_file']
            reader = csv.reader(csv_file)
            idx = 0
            for row in reader:
                slug = slugify(row[0])
                if self.model.objects.filter(txt_idx=slug).count():
                    continue
                obj, c = self.model.objects.get_or_create(
                    label=row[0], txt_idx=slug)
                if c:
                    idx += 1
            self.message_user(request, "Successfully added %d new items." % (
                idx))
            return HttpResponseRedirect(request.get_full_path())
    if not form:
        form = ImportGenericForm(
            initial={'_selected_action':
                     request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    return render_to_response(
        'admin/import_from_csv.html', {'csv_form': form},
        context_instance=RequestContext(request))

gen_import_generic.short_description = "Import from a CSV file"


class HistorizedObjectAdmin(admin.ModelAdmin):
    readonly_fields = ('history_modifier',)

    def save_model(self, request, obj, form, change):
        obj.history_modifier = request.user
        obj.save()


class MyGroupAdmin(GroupAdmin):
    class Media:
        css = {
            "all": ("media/admin.css",)
        }

admin.site.unregister(Group)
admin.site.register(Group, MyGroupAdmin)


class IshtarSiteProfileAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'active', 'files', 'context_record',
                    'find', 'warehouse')
    model = models.IshtarSiteProfile

admin.site.register(models.IshtarSiteProfile, IshtarSiteProfileAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('number', 'label',)
    model = models.Department

admin.site.register(models.Department, DepartmentAdmin)


class OrganizationAdmin(HistorizedObjectAdmin):
    list_display = ('pk', 'name', 'organization_type')
    list_filter = ("organization_type",)
    search_fields = ('name',)
    exclude = ('merge_key', 'merge_exclusion', 'merge_candidate',
               'exclude_from_merge')
    model = models.Organization

admin.site.register(models.Organization, OrganizationAdmin)


class PersonAdmin(HistorizedObjectAdmin):
    list_display = ('pk', 'name', 'surname', 'raw_name', 'email')
    list_filter = ("person_types",)
    search_fields = ('name', 'surname', 'email', 'raw_name')
    exclude = ('merge_key', 'merge_exclusion', 'merge_candidate',
               'exclude_from_merge')
    model = models.Person

admin.site.register(models.Person, PersonAdmin)


class TownAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    search_fields = ['name']
    if settings.COUNTRY == 'fr':
        list_display += ['numero_insee', 'departement', ]
        search_fields += ['numero_insee', 'departement__label', ]
        list_filter = ("departement",)
    model = models.Town

admin.site.register(models.Town, TownAdmin)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ['person', 'author_type']
    list_filter = ("author_type",)
    model = models.Author

admin.site.register(models.Author, AuthorAdmin)


class PersonTypeAdmin(admin.ModelAdmin):
    model = models.PersonType
    filter_vertical = ('groups',)

admin.site.register(models.PersonType, PersonTypeAdmin)


class GlobalVarAdmin(admin.ModelAdmin):
    list_display = ['slug', 'description', 'value']
admin.site.register(models.GlobalVar, GlobalVarAdmin)


class GeneralTypeAdmin(admin.ModelAdmin):
    list_display = ['label', 'txt_idx', 'available']
    actions = ['import_generic']
    import_generic = gen_import_generic


general_models = [models.OrganizationType, models.SourceType,
                  models.AuthorType]
for model in general_models:
    admin.site.register(model, GeneralTypeAdmin)


class ImporterDefaultValuesInline(admin.TabularInline):
    model = models.ImporterDefaultValues


class ImporterDefaultAdmin(admin.ModelAdmin):
    list_display = ('importer_type', 'target')
    model = models.ImporterDefault
    inlines = (ImporterDefaultValuesInline,)
admin.site.register(models.ImporterDefault, ImporterDefaultAdmin)


class ImporterTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'associated_models', 'is_template')
admin.site.register(models.ImporterType, ImporterTypeAdmin)


class RegexpAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', "regexp")
admin.site.register(models.Regexp, RegexpAdmin)


class ImporterDuplicateFieldInline(admin.TabularInline):
    model = models.ImporterDuplicateField


class ImportTargetInline(admin.TabularInline):
    model = models.ImportTarget


class ImporterColumnAdmin(admin.ModelAdmin):
    list_display = ('importer_type', 'col_number', 'description',
                    'targets_lbl', 'duplicate_fields_lbl', 'required')
    list_filter = ('importer_type',)
    inlines = (ImporterDuplicateFieldInline, ImportTargetInline)
admin.site.register(models.ImporterColumn, ImporterColumnAdmin)


class FormaterTypeAdmin(admin.ModelAdmin):
    list_display = ('formater_type', 'options')
admin.site.register(models.FormaterType, FormaterTypeAdmin)


class ImportAdmin(admin.ModelAdmin):
    list_display = ('importer_type', 'imported_file', 'user', 'state',
                    'creation_date')
admin.site.register(models.Import, ImportAdmin)


class TargetKeyAdmin(admin.ModelAdmin):
    list_display = ('target', 'importer_type', 'column_nb', 'key',
                    'value', 'is_set')
    list_filter = ("is_set", "target__column__importer_type")
    search_fields = ('target__target', 'value', 'key')
admin.site.register(models.TargetKey, TargetKeyAdmin)


class OperationTypeAdmin(GeneralTypeAdmin):
    list_display = GeneralTypeAdmin.list_display + ['order', 'preventive']
    model = models.OperationType

admin.site.register(models.OperationType, OperationTypeAdmin)

basic_models = [models.IshtarUser, models.DocumentTemplate]
if settings.COUNTRY == 'fr':
    basic_models += [models.Arrondissement, models.Canton]

for model in basic_models:
    admin.site.register(model)
