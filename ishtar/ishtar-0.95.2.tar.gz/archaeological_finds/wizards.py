#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
from django.core.files.storage import default_storage
from django.utils.translation import ugettext_lazy as _

from ishtar_common.forms import reverse_lazy
from ishtar_common.wizards import Wizard, DeletionWizard, SourceWizard
import models


class FindWizard(Wizard):
    file_storage = default_storage
    model = models.Find
    wizard_done_window = reverse_lazy('show-find')

    def get_current_contextrecord(self):
        step = self.steps.current
        if not step:
            return
        if step.endswith('_creation'):  # a context record has been selected
            main_form_key = 'selecrecord-' + self.url_name
            try:
                idx = int(self.session_get_value(main_form_key, 'pk'))
                current_cr = models.ContextRecord.objects.get(pk=idx)
                return current_cr
            except(TypeError, ValueError, ObjectDoesNotExist):
                pass
        current_item = self.get_current_object()
        if current_item:
            base_finds = current_item.base_finds.all()
            if base_finds:
                return base_finds[0].context_record

    def get_context_data(self, form, **kwargs):
        """
        Get the operation and context record "reminder" on top of wizard forms
        """
        context = super(FindWizard, self).get_context_data(form, **kwargs)
        current_cr = self.get_current_contextrecord()
        if not current_cr or self.steps.current.startswith('select-'):
            return context
        context['reminders'] = (
            (_(u"Operation"), unicode(current_cr.operation)),
            (_(u"Context record"), unicode(current_cr)))
        return context

    def get_extra_model(self, dct, form_list):
        dct = super(FindWizard, self).get_extra_model(dct, form_list)
        dct['order'] = 1
        if 'pk' in dct and type(dct['pk']) == models.ContextRecord:
            dct['base_finds__context_record'] = dct.pop('pk')
        return dct


class FindModificationWizard(FindWizard):
    modification = True
    filter_owns = {'selec-find_modification': ['pk']}


class FindDeletionWizard(DeletionWizard):
    model = models.Find
    fields = ['label', 'material_types', 'datings', 'find_number',
              'object_types', 'description', 'conservatory_state', 'mark',
              'preservation_to_considers', 'integrities', 'volume',
              'weight', 'length', 'width', 'height', 'diameter', 'comment']


class TreatmentWizard(Wizard):
    model = models.Treatment


class FindSourceWizard(SourceWizard):
    model = models.FindSource


class FindSourceDeletionWizard(DeletionWizard):
    model = models.FindSource
    fields = ['item', 'title', 'source_type', 'authors', ]


class TreatmentSourceWizard(SourceWizard):
    model = models.TreatmentSource
