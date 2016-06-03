#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2014-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import datetime

from django import forms
from django.core import validators
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from ishtar_common.models import Person, PersonType, Town, Department, valid_id
from archaeological_files import models

from ishtar_common.forms import get_now, reverse_lazy
from archaeological_files.forms import GENERAL_CONTRACTOR, \
    GENERAL_CONTRACTOR_ORGA, RESPONSIBLE_PLANNING_SERVICE, \
    RESPONSIBLE_PLANNING_SERVICE_ORGA

from ishtar_common import widgets


class FileFormGeneral(forms.Form):
    form_label = _("General")
    associated_models = {'file_type': models.FileType}
    file_type = forms.ChoiceField(label=_("File type"), choices=[])
    year = forms.IntegerField(label=_("Year"),
                              initial=lambda: datetime.datetime.now().year,
                              validators=[validators.MinValueValidator(1900),
                                          validators.MaxValueValidator(2100)])
    creation_date = forms.DateField(label=_(u"Creation date"),
                                    initial=get_now, widget=widgets.JQueryDate)
    reception_date = forms.DateField(
        label=_(u"Reception date"), initial=get_now, widget=widgets.JQueryDate)

    def __init__(self, *args, **kwargs):
        super(FileFormGeneral, self).__init__(*args, **kwargs)
        self.fields['file_type'].choices = models.FileType.get_types()
        self.fields['file_type'].help_text = models.FileType.get_help()

    def clean_reception_date(self):
        value = self.cleaned_data.get('reception_date', None)
        if value and value > datetime.date.today():
            raise forms.ValidationError(
                _('Reception date cannot be after today.'))
        return value


class FileFormPreventiveType(forms.Form):
    form_label = u"Saisine"
    associated_models = {'saisine_type': models.SaisineType,
                         'permit_type': models.PermitType}
    permit_type = forms.ChoiceField(label=_(u"Permit type"), required=False,
                                    choices=[])
    saisine_type = forms.ChoiceField(label=_(u"Saisine type"),
                                     choices=[])

    def __init__(self, *args, **kwargs):
        super(FileFormPreventiveType, self).__init__(*args, **kwargs)
        self.fields['saisine_type'].choices = models.SaisineType.get_types()
        self.fields['saisine_type'].help_text = models.SaisineType.get_help()
        self.fields['permit_type'].choices = \
            models.PermitType.get_types(default='NP')
        self.fields['permit_type'].help_text = models.PermitType.get_help()


class FileFormPlanning(forms.Form):
    form_label = _(u"Planning")
    base_models = ['town', 'department']
    associated_models = {'town': Town, 'department': Department}
    name = forms.CharField(label=_(u"Planning name"), required=False,
                           max_length=100)
    town = widgets.MultipleAutocompleteField(
        model=Town, label=_("Towns"), required=False)
    department = widgets.MultipleAutocompleteField(
        model=Department, label=_("Departments"), required=False)
    locality = forms.CharField(label=_(u"Locality"), max_length=100,
                               required=False)
    address = forms.CharField(
        label=_(u"Address (number/street)"),
        widget=forms.Textarea(attrs={"placeholder": _(u"Number/street")}),
        required=False)
    postal_code = forms.CharField(label=_(u"Postal code"), max_length=10,
                                  required=False)
    total_surface = forms.IntegerField(
        required=False,
        widget=widgets.AreaWidget,
        label=_(u"Total surface (m2)"),
        validators=[validators.MinValueValidator(0),
                    validators.MaxValueValidator(999999999)])
    total_developed_surface = forms.IntegerField(
        widget=widgets.AreaWidget,
        label=_(u"Total developed surface (m2)"),
        required=False,
        validators=[validators.MinValueValidator(0),
                    validators.MaxValueValidator(999999999)])


class FileFormResearchAddress(forms.Form):
    form_label = _(u"Address")
    base_models = ['town', 'department']
    associated_models = {'town': Town, 'department': Department}
    town = widgets.MultipleAutocompleteField(
        model=Town, label=_("Towns"), required=False)
    department = widgets.MultipleAutocompleteField(
        model=Department, label=_("Departments"), required=False)
    locality = forms.CharField(label=_(u"Locality"), max_length=100,
                               required=False)
    address = forms.CharField(
        label=_(u"Address (number/street)"),
        widget=forms.Textarea(attrs={"placeholder": _(u"Number/street")}),
        required=False)
    postal_code = forms.CharField(label=_(u"Postal code"), max_length=10,
                                  required=False)


class PersonOrgaForm(forms.Form):
    PERSON_FIELD = 'TO BE DEFINED'
    PERSON_TYPE = GENERAL_CONTRACTOR
    PERSON_LABEL = ""
    ORGA_FIELD = 'TO BE DEFINED'
    ORGA_TYPE = GENERAL_CONTRACTOR_ORGA
    ORGA_LABEL = ""

    def _media(self):
        if self.status == 'corporation':
            return forms.Media(js=('pdl/JQueryCorporation.js',))
    media = property(_media)

    def __init__(self, *args, **kwargs):
        # get the status: natural person or corporation
        DEFAULT_STATUS = 'natural'
        current_status = ''
        if 'data' in kwargs:
            # the order is important: PERSON can have an ORGA
            for field in [self.ORGA_FIELD, self.PERSON_FIELD]:
                current_item_key = (
                    (kwargs['prefix'] + '-')
                    if kwargs.get('prefix') else '') + field
                if kwargs['data'] and kwargs['data'].get(current_item_key):
                    model = self.associated_models[field]
                    try:
                        model.objects.get(
                            pk=kwargs['data'][current_item_key])
                        current_status = 'natural' \
                            if field == self.PERSON_FIELD else 'corporation'
                    except (model.DoesNotExist, ValueError):
                        pass
        initial = kwargs.get("initial", {})
        if not current_status:
            # the order is important: PERSON can have an ORGA
            for field in [self.ORGA_FIELD, self.PERSON_FIELD]:
                value = initial.get(field)
                model = self.associated_models[field]
                try:
                    model.objects.get(pk=value)
                    current_status = 'natural' if field == self.PERSON_FIELD \
                        else 'corporation'
                except (model.DoesNotExist, ValueError):
                    pass

        status = ''
        if 'status' in kwargs:
            status = kwargs.pop('status')
            if current_status != status:
                if kwargs.get('data'):
                    # status is different from the existing - clear fields
                    kwargs.pop('data')
        elif current_status:
            status = current_status
        else:
            status = DEFAULT_STATUS

        self.status = status

        if status not in ('natural', 'corporation'):
            status = DEFAULT_STATUS

        super(PersonOrgaForm, self).__init__(*args, **kwargs)

        # distinct widget for natural and corporation
        if status == 'natural':
            self.fields[self.PERSON_FIELD] = forms.IntegerField(
                label=self.PERSON_LABEL,
                required=False,
                initial=initial.get(self.PERSON_FIELD, None),
                widget=widgets.JQueryPersonOrganization(
                    reverse_lazy('autocomplete-person',
                                 args=[self.PERSON_TYPE.pk]),
                    reverse_lazy('person_create'),
                    model=Person,
                    limit={'person_types': [self.PERSON_TYPE.pk],
                           'attached_to__isnull': True},
                    js_template='ishtar/blocks/JQueryNaturalPerson.js',
                    new=True),
                validators=[valid_id(Person)])
        else:
            self.fields[self.ORGA_FIELD] = forms.IntegerField(
                label=self.ORGA_LABEL,
                required=False,
                initial=initial.get(self.ORGA_FIELD, None),
                widget=widgets.JQueryPersonOrganization(
                    reverse_lazy('autocomplete-organization',
                                 args=[self.ORGA_TYPE.pk]),
                    reverse_lazy('organization_create'),
                    model=models.Organization,
                    limit={'organization_type': [self.ORGA_TYPE.pk]},
                    js_template='ishtar/blocks/JQueryCorporationPerson.js',
                    new=True),
                validators=[valid_id(models.Organization)])


class FileFormGeneralContractor(PersonOrgaForm):
    form_label = _(u"General contractor")
    associated_models = {'general_contractor': models.Person,
                         'corporation_general_contractor': models.Organization}
    corporation_general_contractor = forms.IntegerField(
        label=_("General contractor"),
        required=False,
        widget=widgets.JQueryPersonOrganization(
            reverse_lazy('autocomplete-organization',
                         args=[GENERAL_CONTRACTOR_ORGA.pk]),
            reverse_lazy('organization_create'),
            model=models.Organization,
            limit={
                'organization_type': [GENERAL_CONTRACTOR_ORGA.pk]
            },
            js_template='ishtar/blocks/JQueryCorporationPerson.js',
            new=True),
        validators=[valid_id(models.Organization)]
    )
    general_contractor = forms.IntegerField(
        label=_(u"In charge"),
        required=False,
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=[GENERAL_CONTRACTOR.pk]),
            associated_model=Person,
            limit={'person_types': [GENERAL_CONTRACTOR.pk]},
            dynamic_limit=['general_contractor'],
            url_new='new-person-noorga',
            new=True),
        validators=[valid_id(Person)]
    )

    PERSON_FIELD = 'general_contractor'
    PERSON_TYPE = GENERAL_CONTRACTOR
    PERSON_LABEL = _(u"General contractor")
    ORGA_FIELD = 'corporation_general_contractor'
    ORGA_TYPE = GENERAL_CONTRACTOR_ORGA
    ORGA_LABEL = _(u"General contractor")

    def __init__(self, *args, **kwargs):
        # get the status: natural person or corporation
        DEFAULT_STATUS = 'natural'
        current_status = ''
        if 'data' in kwargs:
            # the order is important: PERSON can have an ORGA
            for field in [self.PERSON_FIELD, self.ORGA_FIELD]:
                current_item_key = (
                    (kwargs['prefix'] + '-')
                    if kwargs.get('prefix') else '') + field
                if kwargs['data'] and kwargs['data'].get(current_item_key):
                    model = self.associated_models[field]
                    try:
                        model.objects.get(
                            pk=kwargs['data'][current_item_key])
                        current_status = 'natural' \
                            if field == self.PERSON_FIELD else 'corporation'
                    except (model.DoesNotExist, ValueError):
                        pass
        initial = kwargs.get("initial", {})
        if not current_status:
            # the order is important: PERSON can have an ORGA
            for field in [self.ORGA_FIELD, self.PERSON_FIELD]:
                value = initial.get(field)
                model = self.associated_models[field]
                try:
                    model.objects.get(pk=value)
                    current_status = 'natural' if field == self.PERSON_FIELD \
                        else 'corporation'
                except (model.DoesNotExist, ValueError):
                    pass
        status = ''
        if 'status' in kwargs:
            status = kwargs.pop('status')
            if current_status != status:
                if kwargs.get('data'):
                    # status is different from the existing - clear fields
                    kwargs.pop('data')
        elif current_status:
            status = current_status
        else:
            status = DEFAULT_STATUS

        self.status = status

        if status not in ('natural', 'corporation'):
            status = DEFAULT_STATUS

        super(PersonOrgaForm, self).__init__(*args, **kwargs)

        # distinct widget for natural and corporation
        if status == 'natural':
            self.fields[self.PERSON_FIELD] = forms.IntegerField(
                label=self.PERSON_LABEL,
                required=False,
                initial=initial.get(self.PERSON_FIELD, None),
                widget=widgets.JQueryPersonOrganization(
                    reverse_lazy('autocomplete-person',
                                 args=[self.PERSON_TYPE.pk]),
                    reverse_lazy('person_create'),
                    model=Person,
                    limit={'person_types': [self.PERSON_TYPE.pk],
                           'attached_to__isnull': True},
                    js_template='ishtar/blocks/JQueryNaturalPerson.js',
                    new=True),
                validators=[valid_id(Person)])
            self.fields.pop(self.ORGA_FIELD)


class FileFormPlanningService(forms.Form):
    form_label = _(u"Town planning service")
    associated_models = {'responsible_town_planning_service': models.Person,
                         'planning_service': models.Organization}

    permit_reference = forms.CharField(label=_(u"File reference"),
                                       required=False, max_length=200)
    planning_service = forms.IntegerField(
        label=_("Planning service"),
        required=False,
        widget=widgets.JQueryPersonOrganization(
            reverse_lazy('autocomplete-organization',
                         args=[RESPONSIBLE_PLANNING_SERVICE_ORGA.pk]),
            reverse_lazy('organization_create'),
            model=models.Organization,
            limit={
                'organization_type': [RESPONSIBLE_PLANNING_SERVICE_ORGA.pk]
            },
            js_template='ishtar/blocks/JQueryCorporationPerson.js',
            new=True),
        validators=[valid_id(models.Organization)]
    )
    responsible_town_planning_service = forms.IntegerField(
        label=_(u"In charge"),
        required=False,
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=[RESPONSIBLE_PLANNING_SERVICE.pk]),
            associated_model=Person,
            limit={'person_types': [RESPONSIBLE_PLANNING_SERVICE.pk]},
            dynamic_limit=['planning_service'],
            url_new='new-person-noorga',
            new=True),
        validators=[valid_id(Person)]
    )


class FileFormInstruction(forms.Form):
    form_label = u"Instruction SRA"
    associated_models = {'in_charge': models.Person,
                         'related_file': models.File}
    in_charge = forms.IntegerField(
        label=_("Person in charge"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=[PersonType.objects.get(txt_idx='sra_agent').pk]),
            limit={
                'person_types': [
                    PersonType.objects.get(txt_idx='sra_agent').pk]
            },
            associated_model=Person, new=True),
        validators=[valid_id(Person)])
    related_file = forms.IntegerField(
        label=_("Related file"), required=False,
        widget=widgets.JQueryAutoComplete(reverse_lazy('autocomplete-file'),
                                          associated_model=models.File),
        validators=[valid_id(models.File)])
    comment = forms.CharField(label=_(u"Comment"), widget=forms.Textarea,
                              required=False)
    instruction_deadline = forms.DateField(widget=widgets.JQueryDate,
                                           required=False)
    year = forms.IntegerField(label=_("Year"),
                              validators=[validators.MinValueValidator(1900),
                                          validators.MaxValueValidator(2100)])
    numeric_reference = forms.IntegerField(label=_("Numeric reference"),
                                           required=False)
    numeric_reference_is_readonly = True
    end_date = forms.DateField(widget=widgets.JQueryDate, required=False)

    def __init__(self, *args, **kwargs):
        c_year = datetime.date.today().year
        if 'year' in kwargs:
            c_year = kwargs.pop('year')
        saisine_type = None
        if 'saisine_type' in kwargs:
            saisine_type = kwargs.pop('saisine_type')
        reception_date = None
        if 'reception_date' in kwargs:
            reception_date = kwargs.pop('reception_date')
        if 'data' in kwargs and kwargs['data']:
            kwargs['data'][kwargs.get('prefix', '') + '-year'] = c_year

        super(FileFormInstruction, self).__init__(*args, **kwargs)
        self.fields['year'].initial = c_year

        self.fields['year'].widget.attrs.update({'readonly': 'readonly'})
        c_num = 0
        q = models.File.objects.filter(numeric_reference__isnull=False,
                                       year=c_year
                                       ).order_by('-numeric_reference')
        if q.count():
            c_num = q.all()[0].numeric_reference
        lbl = self.fields['numeric_reference'].label
        self.fields['numeric_reference'].label = mark_safe(lbl)
        self.fields['numeric_reference'].initial = c_num + 1
        if self.numeric_reference_is_readonly:
            self.fields['numeric_reference'].widget.attrs['readonly'] = True
            if reception_date and saisine_type:
                if type(reception_date) in (unicode, str):
                    try:
                        reception_date = datetime.datetime.strptime(
                            reception_date, '%d/%m/%Y')
                        self.fields['instruction_deadline'].initial = \
                            (reception_date + datetime.timedelta(
                                days=saisine_type.delay or 0)
                             ).strftime('%Y-%m-%d')
                    except ValueError:
                        pass

        def clean_numeric_reference(self):
            if self.numeric_reference_is_readonly:
                return self.fields['numeric_reference'].initial
            return self.cleaned_data['numeric_reference']


class FileFormInstructionEdit(FileFormInstruction):
    numeric_reference_is_readonly = False
