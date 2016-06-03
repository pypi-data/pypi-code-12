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
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from ishtar_common.forms import reverse_lazy
from ishtar_common.wizards import Wizard, ClosingWizard, DeletionWizard, \
    SourceWizard
import models
from forms import GenerateDocForm

from archaeological_files.models import File


class OperationWizard(Wizard):
    model = models.Operation
    object_parcel_type = 'operation'
    parcel_step_key = 'parcels'
    relations_step_key = 'relations'
    # step contening the current(s) town(s)
    town_step_keys = ['towns-', 'townsgeneral-']
    town_input_id = 'town'  # input id of the current(s) town(s)
    multi_towns = False  # true if current town are multi valued
    towns_formset = True  # true if towns are managed with formset
    wizard_done_window = reverse_lazy('show-operation')

    def get_template_names(self):
        templates = super(OperationWizard, self).get_template_names()
        current_step = self.steps.current
        if current_step.startswith(self.parcel_step_key):
            templates = ['ishtar/wizard/parcels_wizard.html'] + templates
        elif current_step.startswith(self.relations_step_key):
            templates = ['ishtar/wizard/relations_wizard.html'] + templates
        return templates

    def get_current_file(self):
        step = self.steps.current
        if not step:
            return
        file_form_key = 'general-' + self.url_name
        if self.url_name == 'operation_creation':
            file_form_key = 'filechoice-' + self.url_name
        file_id = self.session_get_value(file_form_key, "associated_file")
        try:
            idx = int(file_id)
            current_file = File.objects.get(pk=idx)
            return current_file
        except(TypeError, ValueError, ObjectDoesNotExist):
            pass

    def get_reminder(self):
        archaeological_file = self.get_current_file()
        if archaeological_file:
            return ((_("Archaelogical file"),
                     unicode(archaeological_file)),)

    def get_context_data(self, form, **kwargs):
        """
        Return extra context for templates
        """
        context = super(OperationWizard, self).get_context_data(form,
                                                                **kwargs)
        step = self.steps.current
        if step.startswith('towns'):
            context['TOWNS'] = self.get_towns()
        elif step.startswith('parcels-') and self.get_current_file():
            # if a file is acciated to the operation add the button "Add all"
            context['add_all'] = True
        if step.startswith('parcels') and \
           hasattr(self, 'automatic_parcel_association'):
            context['automatic_parcel_association'] = \
                self.automatic_parcel_association
        # reminder of the current file
        reminder = self.get_reminder()
        if reminder:
            context['reminders'] = reminder
        return context

    def get_towns(self):
        """
        Get available towns
        """
        towns = []
        file = self.get_current_file()
        if not file:
            return -1
        try:
            towns = [(town.pk, unicode(town)) for town in file.towns.all()]
        except (ValueError, ObjectDoesNotExist):
            pass
        return sorted(towns, key=lambda x: x[1])

    def get_available_parcels(self, file):
        self.automatic_parcel_association = False
        parcels = []
        current_parcels = []
        operation = self.get_current_object()
        if operation:
            for parcel in operation.parcels.all():
                current_parcels.append((parcel.town, parcel.section,
                                        parcel.parcel_number))
                parcels.append((parcel.pk, parcel.short_label))
        try:
            for parcel in file.parcels.all():
                key = (parcel.town, parcel.section, parcel.parcel_number)
                if key in current_parcels:
                    current_parcels.pop(current_parcels.index(key))
                    continue
                parcels.append((parcel.pk, parcel.short_label))
            if current_parcels:
                # not all operation parcel exist for the file
                self.automatic_parcel_association = True
        except (ValueError, ObjectDoesNotExist):
            pass
        return sorted(parcels, key=lambda x: x[1])

    def get_form(self, step=None, data=None, files=None):
        """
        Manage specifics fields
        """
        if data:
            data = data.copy()
        else:
            data = {}
        if not step:
            step = self.steps.current
        form = self.get_form_list()[step]
        # manage the dynamic choice of towns
        if step.startswith('towns') and hasattr(form, 'management_form'):
            data['TOWNS'] = self.get_towns()
        elif step.startswith(self.parcel_step_key) \
                and hasattr(form, 'management_form'):
            file = self.get_current_file()
            if file:
                data['PARCELS'] = self.get_available_parcels(file)
            else:
                town_ids = []
                for town_step_key in self.town_step_keys:
                    town_form_key = town_step_key + self.url_name
                    town_ids = self.session_get_value(
                        town_form_key, self.town_input_id,
                        multi=self.towns_formset,
                        multi_value=self.multi_towns) or []
                    if town_ids:
                        towns = []
                        if type(town_ids) == unicode:
                            town_ids = [town_ids]
                        for ids in town_ids:
                            for d in ids.split(','):
                                if d:
                                    towns.append(d)
                        town_ids = towns
                        break
                if type(town_ids) not in (list, tuple):
                    town_ids = [town_ids]
                towns = []
                for town_id in town_ids:
                    try:
                        town = models.Town.objects.get(pk=int(town_id))
                        towns.append((town.pk, unicode(town)))
                    except (ValueError, ObjectDoesNotExist):
                        pass
                data['TOWNS'] = sorted(towns, key=lambda x: x[1])
        data = data or None
        form = super(OperationWizard, self).get_form(step, data, files)
        return form

    def get_formated_datas(self, forms):
        """
        Show a specific warning if no archaelogical file is provided
        """
        datas = super(OperationWizard, self).get_formated_datas(forms)
        # if the general town form is used the advertissement is relevant
        has_no_af = [form.prefix for form in forms
                     if form.prefix == 'townsgeneral-operation'] and True
        if has_no_af:
            datas = [[_(u"Warning: No Archaelogical File is provided. "
                      u"If you have forget it return to the first step."), []]]\
                + datas
        return datas

    def get_form_initial(self, step, data=None):
        initial = super(OperationWizard, self).get_form_initial(step)
        if step == 'general-operation_creation':
            initial.update(self._copy_from_associated_field())
        return initial

    def __copy_fields(self, item, keys):
        initial = {}
        for orig_keys, dest_key in keys:
            value, c_value = None, item
            for orig_key in orig_keys:
                c_value = getattr(c_value, orig_key)
                if not c_value:
                    break
            else:
                value = c_value
            if not value:
                continue
            initial[dest_key] = value
        return initial

    def _copy_from_associated_field(self):
        initial = {}
        file = self.get_current_file()
        if not file:
            return initial
        keys = ((('in_charge', 'pk'), 'in_charge'),
                (('name',), 'common_name'),
                (('total_surface',), 'surface'),
                )
        initial.update(self.__copy_fields(file, keys))
        if file.is_preventive():
            return initial
        keys = ((('scientist', 'pk'), 'scientist'),
                (('requested_operation_type', 'pk'), 'operation_type'),
                (('organization', 'pk'), 'operator'),
                )
        initial.update(self.__copy_fields(file, keys))
        return initial

    def post(self, *args, **kwargs):
        request = self.request
        post_data = request.POST.copy()

        # add all parcel from available in the archaelogical file
        if not post_data.get('add_all_parcels'):
            return super(OperationWizard, self).post(*args, **kwargs)

        file = self.get_current_file()
        if not file:
            return super(OperationWizard, self).post(*args, **kwargs)
        parcel_form_key = self.steps.current
        # parcel_form_key = "parcels-" + self.url_name
        idx = -1
        # remove non relevant deleted keys
        for k in post_data.keys():
            if k.startswith(parcel_form_key) and k.endswith('-DELETE'):
                post_data.pop(k)
        for idx, parcel in enumerate(self.get_available_parcels(file)):
            parcel_pk, parcel_name = parcel
            post_data["%s-%d-parcel" % (parcel_form_key, idx)] = parcel_pk
        post_data[parcel_form_key + '-TOTAL_FORMS'] = idx + 2
        request.POST = post_data
        return super(OperationWizard, self).post(*args, **kwargs)


class OperationModificationWizard(OperationWizard):
    modification = True
    filter_owns = {'selec-operation_modification': ['pk']}


class OperationClosingWizard(ClosingWizard):
    model = models.Operation
    fields = ['year', 'operation_code', 'operation_type', 'associated_file',
              'in_charge', 'scientist', 'start_date', 'excavation_end_date',
              'comment', 'towns', 'remains']


class OperationDeletionWizard(DeletionWizard):
    model = models.Operation
    fields = OperationClosingWizard.fields
    filter_owns = {'selec-operation_deletion': ['pk']}


class OperationSourceWizard(SourceWizard):
    model = models.OperationSource

    def get_form_initial(self, step, data=None):
        initial = super(OperationSourceWizard, self).get_form_initial(step)
        # put default index and operation_id field in the main source form
        general_form_key = 'selec-' + self.url_name
        if step.startswith('source-'):
            operation_id = None
            if self.session_has_key(general_form_key, 'operation'):
                try:
                    operation_id = int(self.session_get_value(general_form_key,
                                                              "operation"))
                except ValueError:
                    pass
            elif self.session_has_key(general_form_key, "pk"):
                try:
                    pk = self.session_get_value(general_form_key, "pk")
                    source = models.OperationSource.objects.get(pk=pk)
                    operation_id = source.operation.pk
                except (ValueError, ObjectDoesNotExist):
                    pass
            if operation_id:
                initial['hidden_operation_id'] = operation_id
                if 'index' not in initial:
                    max_val = models.OperationSource.objects.filter(
                        operation__pk=operation_id).aggregate(
                        Max('index'))["index__max"]
                    initial['index'] = max_val and (max_val + 1) or 1
        return initial


class OperationSourceDeletionWizard(DeletionWizard):
    model = models.OperationSource
    fields = ['operation', 'title', 'source_type', 'authors']


class OperationAdministrativeActWizard(OperationWizard):
    edit = False
    wizard_done_window = reverse_lazy('show-administrativeact')
    current_obj_slug = 'administrativeactop'

    def get_reminder(self):
        form_key = 'selec-' + self.url_name
        if self.url_name.endswith('_administrativeactop'):
            # modification and deletion are suffixed with '_modification'
            # and '_deletion' so it is creation
            operation_id = self.session_get_value(form_key, "pk")
            try:
                return (
                    (_(u"Operation"),
                     unicode(models.Operation.objects.get(pk=operation_id))),
                )
            except models.Operation.DoesNotExist:
                return
        else:
            admin_id = self.session_get_value(form_key, "pk")
            try:
                admin = models.AdministrativeAct.objects.get(pk=admin_id)
                if not admin.operation:
                    return
                return ((_(u"Operation"), unicode(admin.operation)),)
            except models.AdministrativeAct.DoesNotExist:
                return

    def get_extra_model(self, dct, form_list):
        dct['history_modifier'] = self.request.user
        return dct

    def get_context_data(self, form, **kwargs):
        # manage document generation
        context = super(OperationAdministrativeActWizard,
                        self).get_context_data(form, **kwargs)
        step = self.steps.current
        if step.startswith('final-'):
            general_form_key = 'administrativeact-' + self.url_name
            act_type = None
            try:
                act_type = models.ActType.objects.get(
                    pk=self.session_get_value(general_form_key, "act_type"))
            except models.ActType.DoesNotExist:
                pass
            if act_type and act_type.associated_template.count():
                context['extra_form'] = GenerateDocForm(
                    choices=act_type.associated_template.all())
        return context

    def get_associated_item(self, dct):
        return self.get_current_object()

    def save_model(self, dct, m2m, whole_associated_models, form_list,
                   return_object):
        dct['history_modifier'] = self.request.user
        if 'pk' in dct:
            dct.pop('pk')
        if self.edit:
            admact = self.get_current_object()
            for k in dct:
                if hasattr(admact, k):
                    setattr(admact, k, dct[k])
        else:
            associated_item = self.get_associated_item(dct)
            if not associated_item:
                return self.render(form_list[-1])
            if isinstance(associated_item, File):
                dct['associated_file'] = associated_item
            elif isinstance(associated_item, models.Operation):
                dct['operation'] = associated_item
            admact = models.AdministrativeAct(**dct)
        admact.save()
        dct['item'] = admact

        # check if a doc generation is required
        keys = [self.storage.prefix, 'step_data', 'final-' + self.url_name,
                'doc_generation']
        r = self.request.session
        for k in keys:
            if k in r and r[k]:
                r = r[k]
            else:
                break
        if k == keys[-1]:  # the whole list as been traversed
            wizard_done_window = unicode(self.wizard_done_window)
            if wizard_done_window:
                dct['wizard_done_window'] = wizard_done_window
            # redirect to the generated doc
            if r and r[0]:
                dct['redirect'] = reverse('generatedoc-administrativeactop',
                                          args=[admact.pk, r[0]])
        # make the new object a default
        self.request.session[self.current_obj_slug] = unicode(admact.pk)
        self.request.session[self.get_object_name(admact)] = unicode(admact.pk)

        res = render_to_response('ishtar/wizard/wizard_done.html', dct,
                                 context_instance=RequestContext(self.request))
        return res


class OperationEditAdministrativeActWizard(OperationAdministrativeActWizard):
    model = models.AdministrativeAct
    edit = True

    def get_associated_item(self, dct):
        return self.get_current_object().operation


class AdministrativeActDeletionWizard(ClosingWizard):
    wizard_templates = {
        'final-operation_administrativeactop_deletion':
            'ishtar/wizard/wizard_adminact_deletion.html',
        'final-file_administrativeactfile_deletion':
            'ishtar/wizard/wizard_adminact_deletion.html'}
    model = models.AdministrativeAct
    fields = ['act_type', 'in_charge', 'operator', 'scientist', 'signatory',
              'operation', 'associated_file', 'signature_date', 'act_object']
    if settings.COUNTRY == 'fr':
        fields += ['ref_sra']

    def done(self, form_list, **kwargs):
        obj = self.get_current_object()
        obj.delete()
        return render_to_response(
            'ishtar/wizard/wizard_delete_done.html', {},
            context_instance=RequestContext(self.request))


def is_preventive(form_name, model, type_key='operation_type', key=''):
    def func(self):
        request = self.request
        storage = self.storage
        if storage.prefix not in request.session or \
           'step_data' not in request.session[storage.prefix] or \
           form_name not in request.session[storage.prefix]['step_data'] or\
           form_name + '-' + type_key not in \
           request.session[storage.prefix]['step_data'][form_name]:
            return False
        try:
            typ = request.session[storage.prefix][
                'step_data'][form_name][form_name + '-' + type_key]
            if type(typ) in (list, tuple):
                typ = typ[0]
            typ = int(typ)
            return model.is_preventive(typ, key)
        except ValueError:
            return False
    return func


def is_not_preventive(form_name, model, type_key='operation_type', key=''):
    def func(self):
        return not is_preventive(form_name, model, type_key, key)(self)
    return func


def has_associated_file(form_name, file_key='associated_file', negate=False):
    def func(self):
        request = self.request
        storage = self.storage
        if storage.prefix not in request.session or \
           'step_data' not in request.session[storage.prefix] or \
           form_name not in request.session[storage.prefix]['step_data'] or\
           form_name + '-' + file_key not in \
           request.session[storage.prefix]['step_data'][form_name]:
            return negate
        try:
            file_id = request.session[storage.prefix][
                'step_data'][form_name][form_name + '-' + file_key]
            if type(file_id) in (list, tuple):
                file_id = file_id[0]
            file_id = int(file_id)
            return not negate
        except ValueError:
            return negate
    return func
