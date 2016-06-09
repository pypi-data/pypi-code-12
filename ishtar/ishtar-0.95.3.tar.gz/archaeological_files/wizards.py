#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Max
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from ishtar_common.forms import reverse_lazy
from ishtar_common.wizards import ClosingWizard
from archaeological_operations.wizards import OperationWizard,\
    OperationAdministrativeActWizard
from archaeological_operations.models import AdministrativeAct, Parcel, \
    Operation
import models


class FileWizard(OperationWizard):
    model = models.File
    object_parcel_type = 'associated_file'
    parcel_step_key = 'parcels-'
    town_step_keys = ['towns-']
    wizard_done_window = reverse_lazy('show-file')

    def get_extra_model(self, dct, form_list):
        dct = super(FileWizard, self).get_extra_model(dct, form_list)
        if not dct.get('numeric_reference'):
            current_ref = models.File.objects.filter(year=dct['year'])\
                .aggregate(Max('numeric_reference'))["numeric_reference__max"]
            dct['numeric_reference'] = current_ref and current_ref + 1 or 1
        return dct

    def done(self, form_list, **kwargs):
        '''
        Save parcels and make numeric_reference unique
        '''
        r = super(FileWizard, self).done(form_list, return_object=True,
                                         **kwargs)
        if type(r) not in (list, tuple) or len(r) != 2:
            return r
        obj, res = r
        # numeric_reference check
        if not self.modification:
            numeric_reference = obj.numeric_reference
            changed = False
            while obj.__class__.objects.filter(
                    numeric_reference=numeric_reference,
                    year=obj.year).exclude(pk=obj.pk).count():
                numeric_reference += 1
                changed = True
            if changed:
                obj.numeric_reference = numeric_reference
                obj.save()
        obj.parcels.clear()
        for form in form_list:
            if not hasattr(form, 'prefix') \
               or not form.prefix.startswith(self.parcel_step_key) \
               or not hasattr(form, 'forms'):
                continue
            for frm in form.forms:
                if not frm.is_valid():
                    continue
                dct = frm.cleaned_data.copy()
                if 'parcel' in dct:
                    try:
                        parcel = Parcel.objects.get(pk=dct['parcel'])
                        setattr(parcel, self.object_parcel_type, obj)
                        parcel.save()
                    except (ValueError, ObjectDoesNotExist):
                        continue
                    continue
                try:
                    dct['town'] = models.Town.objects.get(pk=int(dct['town']))
                except (ValueError, ObjectDoesNotExist, KeyError):
                    continue
                dct['associated_file'], dct['operation'] = None, None
                dct[self.object_parcel_type] = obj
                if 'DELETE' in dct:
                    dct.pop('DELETE')
                parcel = Parcel.objects.filter(**dct).count()
                if not parcel:
                    dct['history_modifier'] = self.request.user
                    parcel = Parcel(**dct)
                    parcel.save()
        return res


class FileModificationWizard(FileWizard):
    modification = True


class FileClosingWizard(ClosingWizard):
    model = models.File
    fields = ['year', 'numeric_reference', 'internal_reference',
              'file_type', 'in_charge', 'general_contractor', 'creation_date',
              'reception_date', 'total_surface', 'total_developed_surface',
              'address', 'address_complement', 'postal_code', 'comment']
    if settings.COUNTRY == 'fr':
        fields += ['saisine_type', 'permit_reference']
    fields += ['towns']


class FileDeletionWizard(FileClosingWizard):
    def get_formated_datas(self, forms):
        datas = super(FileDeletionWizard, self).get_formated_datas(forms)
        datas.append((_("Associated operations"), []))
        for operation in Operation.objects.filter(
                associated_file=self.current_obj).all():

            if operation.end_date:
                datas[-1][1].append(('', unicode(operation)))
        return datas

    def done(self, form_list, **kwargs):
        obj = self.get_current_object()
        for operation in Operation.objects.filter(associated_file=obj).all():
            operation.delete()
        obj.delete()
        return render_to_response(
            'ishtar/wizard/wizard_delete_done.html', {},
            context_instance=RequestContext(self.request))


class FileAdministrativeActWizard(OperationAdministrativeActWizard):
    model = models.File
    current_obj_slug = 'administrativeactfile'

    def get_reminder(self):
        form_key = 'selec-' + self.url_name
        if self.url_name.endswith('_administrativeactfile'):
            # modification and deletion are suffixed with '_modification'
            # and '_deletion' so it is creation
            file_id = self.session_get_value(form_key, "pk")
            try:
                return (
                    (_(u"Archaelogical file"),
                     unicode(models.File.objects.get(pk=file_id))),)
            except models.File.DoesNotExist:
                return
        else:
            admin_id = self.session_get_value(form_key, "pk")
            try:
                admin = AdministrativeAct.objects.get(pk=admin_id)
                if not admin.associated_file:
                    return
                return ((_(u"Archaelogical file"),
                         unicode(admin.associated_file)),)
            except AdministrativeAct.DoesNotExist:
                return


class FileEditAdministrativeActWizard(FileAdministrativeActWizard):
    model = AdministrativeAct
    edit = True

    def get_associated_item(self, dct):
        return self.get_current_object().associated_file
