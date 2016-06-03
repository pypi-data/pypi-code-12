#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from ishtar_common.forms import reverse_lazy
from ishtar_common.wizards import Wizard, DeletionWizard, SourceWizard
import models


class RecordWizard(Wizard):
    model = models.ContextRecord
    edit = False
    wizard_done_window = reverse_lazy('show-contextrecord')
    relations_step_key = 'relations'

    def get_template_names(self):
        templates = super(RecordWizard, self).get_template_names()
        current_step = self.steps.current
        if current_step.startswith(self.relations_step_key):
            templates = ['ishtar/wizard/relations_wizard.html'] + templates
        return templates

    def get_current_operation(self):
        step = self.steps.current
        if not step:
            return
        # manage manualy on creation
        if step.endswith('_creation'):  # an operation has been selected
            main_form_key = 'selec-' + self.url_name
            try:
                idx = int(self.session_get_value(
                    main_form_key, 'operation_id'))
                current_ope = models.Operation.objects.get(pk=idx)
                return current_ope
            except(TypeError, ValueError, ObjectDoesNotExist):
                pass
        current_cr = self.get_current_object()
        if current_cr:
            return current_cr.operation

    def get_context_data(self, form, **kwargs):
        """
        Get the operation "reminder" on top of wizard forms
        """
        context = super(RecordWizard, self).get_context_data(form)

        operation = self.get_current_operation()
        if not operation or self.steps.current.startswith('selec-'):
            return context
        context['reminders'] = ((_("Operation"), unicode(operation)),)
        return context

    def get_form(self, step=None, data=None, files=None):
        """
        Get associated operation
        """
        if data:
            data = data.copy()
        else:
            data = {}
        if not step:
            step = self.steps.current
            # step = self.determine_step(request, storage)
        form = self.get_form_list()[step]

        # general_form_key = 'general-' + self.url_name
        if step.startswith('general-'):
            if step.endswith('_creation'):  # an operation has been selected
                main_form_key = 'selec-' + self.url_name
                try:
                    idx = int(self.session_get_value(main_form_key,
                                                     'operation_id'))
                    current_obj = models.Operation.objects.get(pk=idx)
                    data['operation'] = current_obj
                except(TypeError, ValueError, ObjectDoesNotExist):
                    pass
            else:
                current_object = self.get_current_object()
                data['context_record'] = current_object
        elif step.startswith('relations') and hasattr(form, 'management_form'):
            data['CONTEXT_RECORDS'] = self.get_other_context_records()
        form = super(RecordWizard, self).get_form(step, data, files)
        return form

    def get_other_context_records(self):
        operation = self.get_current_operation()
        if not operation:
            return []
        q = models.ContextRecord.objects.filter(operation=operation)
        obj = self.get_current_object()
        if obj and obj.pk:
            q = q.exclude(pk=obj.pk)
        return [(cr.pk, unicode(cr)) for cr in q.all()]


class RecordModifWizard(RecordWizard):
    modification = True
    model = models.ContextRecord
    filter_owns = {'selec-record_modification': ['pk']}


class RecordDeletionWizard(DeletionWizard):
    model = models.ContextRecord
    fields = ['label', 'parcel', 'description', 'length', 'width', 'thickness',
              'depth', 'location', 'datings', 'units', 'has_furniture',
              'filling', 'interpretation', 'taq', 'taq_estimated', 'tpq',
              'tpq_estimated']
    filter_owns = {'selec-record_deletion': ['pk']}


class RecordSourceWizard(SourceWizard):
    model = models.ContextRecordSource


class RecordSourceDeletionWizard(DeletionWizard):
    model = models.ContextRecordSource
    fields = ['context_record', 'title', 'source_type', 'authors', ]
