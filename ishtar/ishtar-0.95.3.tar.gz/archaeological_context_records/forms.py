#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
Context records forms definitions
"""
from itertools import groupby

from django import forms
from django.conf import settings
from django.core import validators
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext_lazy as _

from ishtar_common.models import valid_id
from archaeological_operations.models import Period, Parcel, Operation, \
    ArchaeologicalSite
import models

from ishtar_common import widgets
from ishtar_common.forms import FinalForm, FormSet, \
    reverse_lazy, get_form_selection, TableSelect
from ishtar_common.forms_common import get_town_field, SourceSelect
from archaeological_operations.forms import OperationSelect, ParcelField,\
    RecordRelationsForm as OpeRecordRelationsForm


class RecordSelect(TableSelect):
    label = forms.CharField(label=_(u"ID"), max_length=100)
    parcel__town = get_town_field()
    if settings.COUNTRY == 'fr':
        operation__code_patriarche = forms.IntegerField(
            label=_(u"Code PATRIARCHE"))
    operation__year = forms.IntegerField(label=_(u"Operation's year"))
    operation__operation_code = forms.IntegerField(
        label=_(u"Operation's number (index by year)"))
    archaeological_sites = forms.IntegerField(
        label=_("Archaelogical site"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-archaeologicalsite'),
            associated_model=ArchaeologicalSite),
        validators=[valid_id(ArchaeologicalSite)])
    datings__period = forms.ChoiceField(label=_(u"Period"), choices=[])
    unit = forms.ChoiceField(label=_(u"Unit type"), choices=[])
    parcel = ParcelField(label=_(u"Parcel (section/number)"))
    relation_types = forms.MultipleChoiceField(
        label=_(u"Search within relations"), choices=[],
        widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(RecordSelect, self).__init__(*args, **kwargs)
        self.fields['datings__period'].choices = Period.get_types()
        self.fields['datings__period'].help_text = Period.get_help()
        self.fields['unit'].choices = models.Unit.get_types()
        self.fields['unit'].help_text = models.Unit.get_help()
        self.fields['relation_types'].choices = models.RelationType.get_types(
            empty_first=False)

    def get_input_ids(self):
        ids = super(RecordSelect, self).get_input_ids()
        ids.pop(ids.index('parcel'))
        ids.append('parcel_0')
        ids.append('parcel_1')
        ids.pop(ids.index('relation_types'))
        for idx, c in enumerate(self.fields['relation_types'].choices):
            ids.append('relation_types_{}'.format(idx))
        return ids


class RecordFormSelection(forms.Form):
    form_label = _("Context record search")
    associated_models = {'pk': models.ContextRecord}
    currents = {'pk': models.ContextRecord}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-contextrecord'),
            RecordSelect, models.ContextRecord,
            source_full=reverse_lazy('get-contextrecord-full')),
        validators=[valid_id(models.ContextRecord)])

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'pk' not in cleaned_data or not cleaned_data['pk']:
            raise forms.ValidationError(_(u"You should at least select one "
                                          u"context record."))
        return cleaned_data


class RecordFormGeneral(forms.Form):
    form_label = _("General")
    associated_models = {'parcel': Parcel, 'unit': models.Unit}
    pk = forms.IntegerField(required=False, widget=forms.HiddenInput)
    operation_id = forms.IntegerField(widget=forms.HiddenInput)
    parcel = forms.ChoiceField(label=_("Parcel"), choices=[])
    label = forms.CharField(label=_(u"ID"),
                            validators=[validators.MaxLengthValidator(200)])
    description = forms.CharField(label=_(u"Description"),
                                  widget=forms.Textarea, required=False)
    length = forms.IntegerField(label=_(u"Length (cm)"), required=False)
    width = forms.IntegerField(label=_(u"Width (cm)"), required=False)
    thickness = forms.IntegerField(label=_(u"Thickness (cm)"), required=False)
    depth = forms.IntegerField(label=_(u"Depth (cm)"), required=False)
    unit = forms.ChoiceField(label=_("Unit"), required=False, choices=[])
    location = forms.CharField(
        label=_(u"Location"), widget=forms.Textarea,
        required=False, validators=[validators.MaxLengthValidator(200)])

    def __init__(self, *args, **kwargs):
        operation = None
        if 'data' in kwargs and kwargs['data'] and \
                ('operation' in kwargs['data'] or
                 'context_record' in kwargs['data']):
            if 'operation' in kwargs['data']:
                operation = kwargs['data']['operation']
            if 'context_record' in kwargs['data'] and \
               kwargs['data']['context_record']:
                operation = kwargs['data']['context_record'].operation
            # clean data if not "real" data
            # prefix_value = kwargs['prefix']
            if not [k for k in kwargs['data'].keys()
                    if k.startswith(kwargs['prefix']) and kwargs['data'][k]]:
                kwargs['data'] = None
                if 'files' in kwargs:
                    kwargs.pop('files')
        super(RecordFormGeneral, self).__init__(*args, **kwargs)
        self.fields['parcel'].choices = [('', '--')]
        if operation:
            self.fields['operation_id'].initial = operation.pk
            parcels = operation.parcels.all()
            sort = lambda x: (x.town.name, x.section)
            parcels = sorted(parcels, key=sort)
            for key, gparcels in groupby(parcels, sort):
                self.fields['parcel'].choices.append(
                    (" - ".join(key), [(parcel.pk, parcel.short_label)
                                       for parcel in gparcels])
                )
        self.fields['unit'].choices = models.Unit.get_types()
        self.fields['unit'].help_text = models.Unit.get_help()

    def clean(self):
        # manage unique context record ID
        cleaned_data = self.cleaned_data
        operation_id = cleaned_data.get("operation_id")
        label = cleaned_data.get("label")
        cr = models.ContextRecord.objects.filter(
            label=label, parcel__operation__pk=operation_id)
        if 'pk' in cleaned_data and cleaned_data['pk']:
            cr = cr.exclude(pk=cleaned_data['pk'])
        if cr.count():
            raise forms.ValidationError(_(u"This ID already exists for "
                                          u"this operation."))
        return cleaned_data


class DatingForm(forms.Form):
    form_label = _("Dating")
    base_model = 'dating'
    associated_models = {'dating_type': models.DatingType,
                         'quality': models.DatingQuality,
                         'period': models.Period}
    period = forms.ChoiceField(label=_("Period"), choices=[])
    start_date = forms.IntegerField(label=_(u"Start date"), required=False)
    end_date = forms.IntegerField(label=_(u"End date"), required=False)
    quality = forms.ChoiceField(label=_("Quality"), required=False, choices=[])
    dating_type = forms.ChoiceField(label=_("Dating type"), required=False,
                                    choices=[])

    def __init__(self, *args, **kwargs):
        super(DatingForm, self).__init__(*args, **kwargs)
        self.fields['dating_type'].choices = models.DatingType.get_types()
        self.fields['dating_type'].help_text = models.DatingType.get_help()
        self.fields['quality'].choices = models.DatingQuality.get_types()
        self.fields['quality'].help_text = models.DatingQuality.get_help()
        self.fields['period'].choices = Period.get_types()
        self.fields['period'].help_text = Period.get_help()


DatingFormSet = formset_factory(DatingForm, can_delete=True,
                                formset=FormSet)
DatingFormSet.form_label = _("Dating")


class RecordRelationsForm(OpeRecordRelationsForm):
    current_model = models.RelationType
    current_related_model = models.ContextRecord
    associated_models = {'right_record': models.ContextRecord,
                         'relation_type': models.RelationType}
    right_record = forms.ChoiceField(
        label=_(u"Context record"), choices=[], required=False)

    def __init__(self, *args, **kwargs):
        crs = None
        if 'data' in kwargs and 'CONTEXT_RECORDS' in kwargs['data']:
            crs = kwargs['data']['CONTEXT_RECORDS']
            # clean data if not "real" data
            prefix_value = kwargs['prefix'] + '-right_record'
            if not [k for k in kwargs['data'].keys()
                    if k.startswith(prefix_value) and kwargs['data'][k]]:
                kwargs['data'] = None
                if 'files' in kwargs:
                    kwargs.pop('files')
        super(RecordRelationsForm, self).__init__(*args, **kwargs)
        self.fields['relation_type'].choices = \
            models.RelationType.get_types()
        if crs:
            self.fields['right_record'].choices = [('', '-' * 2)] + crs

RecordRelationsFormSet = formset_factory(RecordRelationsForm, can_delete=True)
RecordRelationsFormSet.form_label = _(u"Relations")


class RecordFormInterpretation(forms.Form):
    form_label = _("Interpretation")
    associated_models = {'activity': models.ActivityType,
                         'identification': models.IdentificationType}
    has_furniture = forms.NullBooleanField(label=_(u"Has furniture?"),
                                           required=False)
    filling = forms.CharField(label=_(u"Filling"),
                              widget=forms.Textarea, required=False)
    interpretation = forms.CharField(label=_(u"Interpretation"),
                                     widget=forms.Textarea, required=False)
    activity = forms.ChoiceField(label=_(u"Activity"), required=False,
                                 choices=[])
    identification = forms.ChoiceField(label=_("Identification"),
                                       required=False, choices=[])
    taq = forms.IntegerField(label=_(u"TAQ"), required=False)
    taq_estimated = forms.IntegerField(label=_(u"Estimated TAQ"),
                                       required=False)
    tpq = forms.IntegerField(label=_(u"TPQ"), required=False)
    tpq_estimated = forms.IntegerField(label=_(u"Estimated TPQ"),
                                       required=False)

    def __init__(self, *args, **kwargs):
        super(RecordFormInterpretation, self).__init__(*args, **kwargs)
        self.fields['activity'].choices = models.ActivityType.get_types()
        self.fields['activity'].help_text = models.ActivityType.get_help()
        self.fields['identification'].choices = \
            models.IdentificationType.get_types()
        self.fields['identification'].help_text = \
            models.IdentificationType.get_help()

OperationRecordFormSelection = get_form_selection(
    'OperationRecordFormSelection', _(u"Operation search"), 'operation_id',
    Operation, OperationSelect, 'get-operation',
    _(u"You should select an operation."))


class RecordDeletionForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to delete this context record?")

#########################################
# Source management for context records #
#########################################

SourceRecordFormSelection = get_form_selection(
    'SourceRecordFormSelection', _(u"Context record search"),
    'context_record', models.ContextRecord, RecordSelect, 'get-contextrecord',
    _(u"You should select a context record."))


class RecordSourceSelect(SourceSelect):
    context_record__parcel__town = get_town_field(
        label=_(u"Town of the operation"))
    context_record__operation__year = forms.IntegerField(
        label=_(u"Year of the operation"))
    context_record__datings__period = forms.ChoiceField(
        label=_(u"Period of the context record"), choices=[])
    context_record__unit = forms.ChoiceField(
        label=_(u"Unit type of the context record"), choices=[])

    def __init__(self, *args, **kwargs):
        super(RecordSourceSelect, self).__init__(*args, **kwargs)
        self.fields['context_record__datings__period'].choices = \
            Period.get_types()
        self.fields['context_record__datings__period'].help_text = \
            Period.get_help()
        self.fields['context_record__unit'].choices = models.Unit.get_types()
        self.fields['context_record__unit'].help_text = models.Unit.get_help()


RecordSourceFormSelection = get_form_selection(
    'RecordSourceFormSelection', _(u"Documentation search"), 'pk',
    models.ContextRecordSource, RecordSourceSelect, 'get-contextrecordsource',
    _(u"You should select a document."),
    get_full_url='get-contextrecordsource-full')
