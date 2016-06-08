#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from archaeological_files.wizards import FileWizard as BaseFileWizard
from archaeological_files import models


class FileWizard(BaseFileWizard):
    parcel_step_key = 'parcelspdl-'
    town_step_keys = ['preventiveplanning-', 'researchaddress-']
    town_input_id = 'town'
    towns_formset = False
    multi_towns = True
    wizard_templates = {
        'generalcontractor-%(url_name)s':
            'ishtar/wizard/wizard_generalcontractor.html',
        'planningservice-%(url_name)s':
            'ishtar/wizard/wizard_planningservice.html',
        'instruction-%(url_name)s':
            'ishtar/wizard/wizard_instruction.html',
        'preventiveplanning-%(url_name)s':
            'ishtar/wizard/wizard_preventiveplanning.html',
    }
    wizard_confirm = 'ishtar/wizard/file_confirm_wizard.html'

    def get_current_year(self):
        general_form_key = 'general-' + self.url_name
        return self.session_get_value(general_form_key, 'year')

    def get_form_kwargs(self, *args, **kwargs):
        returned = super(FileWizard, self).get_form_kwargs(*args, **kwargs)
        if args and args[0].startswith('generalcontractor-'):
            if 'status' in self.request.GET:
                returned['status'] = self.request.GET['status']
        if args and args[0].startswith('instruction-'):
            returned['year'] = self.get_current_year()
            returned['saisine_type'] = self.get_saisine_type()
            returned['reception_date'] = \
                self.session_get_value(
                    'general-' + self.url_name, 'reception_date')
        return returned

    def get_saisine_type(self):
        try:
            idx = int(
                self.session_get_value(
                    'preventivetype-' + self.url_name, 'saisine_type'))
            return models.SaisineType.objects.get(pk=idx)
        except (TypeError, ValueError, models.PermitType.DoesNotExist):
            pass

    def get_context_data(self, form, **kwargs):
        context = super(FileWizard, self).get_context_data(form)
        formplanning = "planningservice-" + self.url_name
        forminstruction = "instruction-" + self.url_name
        formfinal = "final-" + self.url_name
        if self.steps.current == formplanning:
            try:
                idx = int(
                    self.session_get_value(
                        'preventivetype-' + self.url_name, 'permit_type'))
                permit_type = models.PermitType.objects.get(pk=idx)
                context['permit_type'] = unicode(permit_type)
                context['permit_type_code'] = unicode(permit_type.txt_idx)
            except (TypeError, ValueError, models.PermitType.DoesNotExist):
                pass
        elif self.steps.current == forminstruction:
            saisine_type = self.get_saisine_type()
            if saisine_type:
                context['saisine_type'] = unicode(saisine_type)
                context['saisine_type_delay'] = saisine_type.delay or 0
        elif self.steps.current == formfinal:
            if self.steps.current.endswith('creation'):  # creation only
                parcels = []
                parcel_step_key = self.parcel_step_key + self.url_name

                parcel_numbers = self.session_get_value(
                    parcel_step_key, 'parcel_number', multi=True) or []
                sections = self.session_get_value(
                    parcel_step_key, 'section', multi=True) or []
                towns = self.session_get_value(
                    parcel_step_key, 'town', multi=True) or []
                for idx, parcel_number in enumerate(parcel_numbers):
                    if not parcel_number:
                        continue
                    parcels.append({
                        'town': towns[idx],
                        'section': sections[idx],
                        'parcel_number': parcel_number})
                context['similar_files'] = models.File.similar_files(parcels)
            else:  # edition only
                try:
                    numeric_reference = int(
                        self.session_get_value(
                            'instruction-' + self.url_name,
                            'numeric_reference'))

                    q = models.File.objects.filter(
                        numeric_reference=numeric_reference,
                        year=self.get_current_year()).exclude(
                        pk=self.get_current_object().pk)
                    context['numeric_reference_files'] = q.all()
                except ValueError:
                    pass

        return context


class FileModificationWizard(FileWizard):
    modification = True
