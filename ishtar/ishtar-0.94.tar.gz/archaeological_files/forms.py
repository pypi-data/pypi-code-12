#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
Files forms definitions
"""
import datetime

from django import forms
from django.conf import settings
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from ishtar_common.models import Person, PersonType, Organization, \
    OrganizationType, valid_id, Department
from archaeological_operations.models import ActType, AdministrativeAct, \
    OperationType
import models
from ishtar_common.forms import FinalForm, get_now, reverse_lazy, TableSelect
from ishtar_common.forms_common import get_town_field
from archaeological_operations.forms import AdministrativeActOpeForm, \
    AdministrativeActOpeFormSelection, \
    ParcelField, SLICING, HEAD_SCIENTIST, SRA_AGENT
from ishtar_common import widgets

GENERAL_CONTRACTOR, created = PersonType.objects.get_or_create(
    txt_idx='general_contractor')

GENERAL_CONTRACTOR_ORGA, created = OrganizationType.objects.get_or_create(
    txt_idx='general_contractor')


class FileSelect(TableSelect):
    year = forms.IntegerField(label=_("Year"))
    numeric_reference = forms.IntegerField(label=_("Numeric reference"))
    internal_reference = forms.CharField(max_length=200,
                                         label=_("Other reference"))
    towns = get_town_field()
    parcel = ParcelField(label=_("Parcel (section/number)"))
    if settings.ISHTAR_DPTS:
        towns__numero_insee__startswith = forms.ChoiceField(
            label=_(u"Department"), choices=[])
    name = forms.CharField(label=_(u"File name"), max_length=200)
    file_type = forms.ChoiceField(label=_("File type"), choices=[])
    end_date = forms.NullBooleanField(label=_(u"Is active?"))
    saisine_type = forms.ChoiceField(label=_("Saisine type"), choices=[])
    permit_type = forms.ChoiceField(label=_("Permit type"), choices=[])
    permit_reference = forms.CharField(max_length=200,
                                       label=_("Permit reference"))
    comment = forms.CharField(label=_(u"Comment"), max_length=500)
    in_charge = forms.IntegerField(
        label=_(u"In charge"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=[SRA_AGENT.pk]),
            associated_model=Person),
        validators=[valid_id(Person)])
    general_contractor = forms.IntegerField(
        label=_(u"General contractor"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=[GENERAL_CONTRACTOR.pk]),
            associated_model=Person),
        validators=[valid_id(Person)])
    general_contractor__attached_to = forms.IntegerField(
        label=_(u"Organization of general contractor"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-organization',
                         args=[GENERAL_CONTRACTOR_ORGA.pk]),
            associated_model=Organization),
        validators=[valid_id(Organization)])
    history_creator = forms.IntegerField(
        label=_(u"Created by"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=['0', 'user']),
            associated_model=Person),
        validators=[valid_id(Person)])
    history_modifier = forms.IntegerField(
        label=_(u"Modified by"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=['0', 'user']),
            associated_model=Person),
        validators=[valid_id(Person)])

    def __init__(self, *args, **kwargs):
        super(FileSelect, self).__init__(*args, **kwargs)
        self.fields['saisine_type'].choices = models.SaisineType.get_types()
        self.fields['saisine_type'].help_text = models.SaisineType.get_help()
        self.fields['permit_type'].choices = models.PermitType.get_types()
        self.fields['permit_type'].help_text = models.PermitType.get_help()
        self.fields['file_type'].choices = models.FileType.get_types()
        self.fields['file_type'].help_text = models.FileType.get_help()
        if settings.ISHTAR_DPTS:
            k = 'towns__numero_insee__startswith'
            self.fields[k].choices = [
                ('', '--')] + list(settings.ISHTAR_DPTS)

    def get_input_ids(self):
        ids = super(FileSelect, self).get_input_ids()
        ids.pop(ids.index('parcel'))
        ids.append('parcel_0')
        ids.append('parcel_1')
        return ids


class FileFormSelection(forms.Form):
    form_label = _("Archaeological file search")
    associated_models = {'pk': models.File}
    currents = {'pk': models.File}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-file'),
            FileSelect, models.File,
            source_full=reverse_lazy('get-file-full')),
        validators=[valid_id(models.File)])

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'pk' not in cleaned_data or not cleaned_data['pk']:
            raise forms.ValidationError(_(u"You should select a file."))
        return cleaned_data

DATE_SOURCE = (('creation', _(u"Creation date")),
               ("reception", _(u"Reception date")))


class DashboardForm(forms.Form):
    slicing = forms.ChoiceField(
        label=_("Slicing"), choices=SLICING, required=False)
    department_detail = forms.BooleanField(
        label=_("Department detail"), required=False)
    date_source = forms.ChoiceField(
        label=_("Date get from"), choices=DATE_SOURCE, required=False)
    file_type = forms.ChoiceField(
        label=_("File type"), choices=[], required=False)
    saisine_type = forms.ChoiceField(
        label=_("Saisine type"), choices=[], required=False)
    after = forms.DateField(
        label=_(u"Date after"), widget=widgets.JQueryDate, required=False)
    before = forms.DateField(
        label=_(u"Date before"), widget=widgets.JQueryDate, required=False)

    def __init__(self, *args, **kwargs):
        if 'prefix' not in kwargs:
            kwargs['prefix'] = 'files'
        super(DashboardForm, self).__init__(*args, **kwargs)
        self.fields['saisine_type'].choices = models.SaisineType.get_types()
        self.fields['file_type'].choices = models.FileType.get_types()

    def get_show_detail(self):
        return hasattr(self, 'cleaned_data') and \
            self.cleaned_data.get('department_detail')

    def get_date_source(self):
        date_source = 'creation'
        if hasattr(self, 'cleaned_data') and \
           self.cleaned_data.get('date_source'):
            date_source = self.cleaned_data['date_source']
        return date_source

    def get_filter(self):
        if not hasattr(self, 'cleaned_data') or not self.cleaned_data:
            return {}
        date_source = self.get_date_source()
        fltr = {}
        if self.cleaned_data.get('saisine_type'):
            fltr['saisine_type_id'] = self.cleaned_data['saisine_type']
        if self.cleaned_data.get('file_type'):
            fltr['file_type_id'] = self.cleaned_data['file_type']
        if self.cleaned_data.get('after'):
            fltr[date_source + '_date__gte'] = self.cleaned_data['after']
        if self.cleaned_data.get('before'):
            fltr[date_source + '_date__lte'] = self.cleaned_data['before']
        return fltr


class FileFormGeneral(forms.Form):
    form_label = _("General")
    associated_models = {'in_charge': Person,
                         'related_file': models.File,
                         'file_type': models.FileType}
    in_charge = forms.IntegerField(
        label=_("Person in charge"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person', args=[SRA_AGENT.pk]),
            limit={'person_types': [SRA_AGENT.pk]},
            associated_model=Person, new=True),
        validators=[valid_id(Person)])
    year = forms.IntegerField(label=_("Year"),
                              initial=lambda: datetime.datetime.now().year,
                              validators=[validators.MinValueValidator(1900),
                                          validators.MaxValueValidator(2100)])
    numeric_reference = forms.IntegerField(
        label=_("Numeric reference"), widget=forms.HiddenInput, required=False)
    internal_reference = forms.CharField(
        label=_(u"Other reference"), max_length=60, required=False)
    name = forms.CharField(label=_(u"Name"), required=False, max_length=100)
    creation_date = forms.DateField(label=_(u"Creation date"),
                                    initial=get_now, widget=widgets.JQueryDate)
    file_type = forms.ChoiceField(label=_("File type"), choices=[])
    related_file = forms.IntegerField(
        label=_("Related file"), required=False,
        widget=widgets.JQueryAutoComplete(reverse_lazy('autocomplete-file'),
                                          associated_model=models.File),
        validators=[valid_id(models.File)])
    comment = forms.CharField(label=_(u"Comment"), widget=forms.Textarea,
                              required=False)
    total_surface = forms.IntegerField(
        required=False, widget=widgets.AreaWidget,
        label=_(u"Total surface (m2)"),
        validators=[validators.MinValueValidator(0),
                    validators.MaxValueValidator(999999999)])
    address = forms.CharField(label=_(u"Main address"), widget=forms.Textarea)
    address_complement = forms.CharField(label=_(u"Main address - complement"),
                                         required=False)

    def __init__(self, *args, **kwargs):
        super(FileFormGeneral, self).__init__(*args, **kwargs)
        self.fields['file_type'].choices = models.FileType.get_types()
        self.fields['file_type'].help_text = models.FileType.get_help()
        q = models.File.objects\
                  .filter(internal_reference__isnull=False)\
                  .exclude(internal_reference='').order_by('-pk')
        if q.count():
            lbl = self.fields['internal_reference'].label
            lbl += _(u"<br/>(last recorded: %s)") % (
                q.all()[0].internal_reference)
            self.fields['internal_reference'].label = mark_safe(lbl)


class FileFormGeneralRO(FileFormGeneral):
    year = forms.IntegerField(
        label=_(u"Year"), widget=forms.TextInput(attrs={'readonly': True}))
    numeric_reference = forms.IntegerField(
        label=_(u"Numeric reference"), widget=forms.TextInput())
    id = forms.IntegerField(' ', widget=forms.HiddenInput, required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        year = cleaned_data.get('year')
        pk = cleaned_data.get('id')
        numeric_reference = cleaned_data.get('numeric_reference')
        q = models.File.objects\
                       .filter(year=year, numeric_reference=numeric_reference)\
                       .exclude(pk=pk)
        if numeric_reference and q.count():
            raise forms.ValidationError(
                _(u"Another file with this numeric id exists."))
        return cleaned_data

RESPONSIBLE_PLANNING_SERVICE, created = PersonType.objects.get_or_create(
    txt_idx='responsible_planning_service')

RESPONSIBLE_PLANNING_SERVICE_ORGA, created = \
    OrganizationType.objects.get_or_create(txt_idx='planning_service')


class FileFormPreventive(forms.Form):
    form_label = _(u"Preventive informations")
    associated_models = {'general_contractor': Person,
                         'saisine_type': models.SaisineType,
                         'permit_type': models.PermitType,
                         'responsible_town_planning_service': Person}
    general_contractor = forms.IntegerField(
        label=_(u"General contractor"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=[PersonType.objects.get(txt_idx='general_contractor').pk]
            ),
            limit={'person_types': [
                PersonType.objects.get(txt_idx='general_contractor').pk]},
            associated_model=Person, new=True),
        validators=[valid_id(Person)])
    responsible_town_planning_service = forms.IntegerField(
        required=False,
        label=_(u"Responsible for town planning service"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=[RESPONSIBLE_PLANNING_SERVICE.pk]
            ),
            limit={'person_types': [
                RESPONSIBLE_PLANNING_SERVICE.pk]},
            associated_model=Person, new=True),
        validators=[valid_id(Person)])
    permit_type = forms.ChoiceField(label=_(u"Permit type"), required=False,
                                    choices=[])
    permit_reference = forms.CharField(
        label=_(u"Permit reference"), required=False,
        validators=[validators.MaxLengthValidator(60)])
    total_developed_surface = forms.IntegerField(
        widget=widgets.AreaWidget, label=_(u"Total developed surface (m2)"),
        required=False, validators=[validators.MinValueValidator(0),
                                    validators.MaxValueValidator(999999999)])
    if settings.COUNTRY == 'fr':
        saisine_type = forms.ChoiceField(label=_(u"Saisine type"),
                                         choices=[])
    reception_date = forms.DateField(
        label=_(u"Reception date"), initial=get_now, widget=widgets.JQueryDate)

    def __init__(self, *args, **kwargs):
        super(FileFormPreventive, self).__init__(*args, **kwargs)
        self.fields['saisine_type'].choices = models.SaisineType.get_types()
        self.fields['saisine_type'].help_text = models.SaisineType.get_help()
        self.fields['permit_type'].choices = models.PermitType.get_types(
            default='NP')
        self.fields['permit_type'].help_text = models.PermitType.get_help()


class FileFormResearch(forms.Form):
    form_label = _("Research archaeology")
    base_model = 'department'
    associated_models = {'scientist': Person,
                         'requested_operation_type': OperationType,
                         'organization': Organization,
                         'department': Department}
    department = widgets.MultipleAutocompleteField(
        model=Department,
        label=_("Departments"),
        required=False)
    scientist = forms.IntegerField(
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=["_".join([unicode(HEAD_SCIENTIST.pk),
                                unicode(SRA_AGENT.pk)])]),
                limit={'person_types': [unicode(HEAD_SCIENTIST.pk),
                                        unicode(SRA_AGENT.pk)]},
            associated_model=Person, new=True),
        label=_(u"Scientist in charge"))
    requested_operation_type = forms.ChoiceField(
        label=_(u"Requested operation type"), choices=[])
    organization = forms.IntegerField(
        label=_(u"Lead organization"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-organization'),
            associated_model=Organization, new=True),
        validators=[valid_id(Organization)], required=False)
    if settings.COUNTRY == 'fr':
        cira_advised = forms.NullBooleanField(label=u"Passage en CIRA",
                                              required=False)
    research_comment = forms.CharField(
        label=_(u"Comment"), widget=forms.Textarea, required=False)
    if settings.COUNTRY == 'fr':
        mh_register = forms.NullBooleanField(
            label=u"Sur Monument Historique classé", required=False)
        mh_listing = forms.NullBooleanField(
            label=u"Sur Monument Historique inscrit", required=False)
    classified_area = forms.NullBooleanField(
        label=_(u"Classified area"), required=False)
    protected_area = forms.NullBooleanField(
        label=_(u"Protected area"), required=False)

    def __init__(self, *args, **kwargs):
        super(FileFormResearch, self).__init__(*args, **kwargs)
        self.fields['requested_operation_type'].choices = \
            OperationType.get_types(dct={"preventive": False})
        self.fields['requested_operation_type'].help_text = \
            OperationType.get_help()


class FinalFileClosingForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to close this archaeological file?")


class FinalFileDeleteForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to delete this archaelogical file ?")


class AdministrativeActFileModifySelect(TableSelect):
    year = forms.IntegerField(label=_("Year"))
    index = forms.IntegerField(label=_("Index"))
    if settings.COUNTRY == 'fr':
        ref_sra = forms.CharField(label=u"Référence SRA",
                                  max_length=15)
    act_type = forms.ChoiceField(label=_("Act type"), choices=[])
    act_object = forms.CharField(label=_(u"Object (full text search)"),
                                 max_length=300)
    operation__towns = get_town_field()
    if settings.ISHTAR_DPTS:
        operation__towns__numero_insee__startswith = forms.ChoiceField(
            label=_(u"Department"), choices=[])

    def __init__(self, *args, **kwargs):
        super(AdministrativeActFileModifySelect, self).__init__(*args,
                                                                **kwargs)
        self.fields['act_type'].choices = ActType.get_types(
            dct={'intented_to': 'F'})
        self.fields['act_type'].help_text = ActType.get_help(
            dct={'intented_to': 'F'})
        if settings.ISHTAR_DPTS:
            k = 'operation__towns__numero_insee__startswith'
            self.fields[k].choices = [
                ('', '--')] + list(settings.ISHTAR_DPTS)


class AdministrativeActFileSelect(TableSelect):
    year = forms.IntegerField(label=_("Year"))
    index = forms.IntegerField(label=_("Index"))
    if settings.COUNTRY == 'fr':
        ref_sra = forms.CharField(label=u"Autre référence",
                                  max_length=15)
    act_type = forms.ChoiceField(label=_("Act type"), choices=[])
    indexed = forms.NullBooleanField(label=_(u"Indexed?"))
    associated_file__towns = get_town_field()
    parcel = ParcelField(label=_("Parcel (section/number)"))
    if settings.ISHTAR_DPTS:
        associated_file__towns__numero_insee__startswith = forms.ChoiceField(
            label=_(u"Department"), choices=[])
    act_object = forms.CharField(label=_(u"Object"),
                                 max_length=300)

    signature_date_after = forms.DateField(
        label=_(u"Signature date after"), widget=widgets.JQueryDate)
    signature_date_before = forms.DateField(
        label=_(u"Signature date before"), widget=widgets.JQueryDate)
    associated_file__name = forms.CharField(
        label=_(u"File name"), max_length=200)
    associated_file__general_contractor = forms.IntegerField(
        label=_(u"General contractor"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=[
                    PersonType.objects.get(txt_idx='general_contractor').pk]),
                associated_model=Person),
        validators=[valid_id(Person)])
    associated_file__general_contractor__attached_to = forms.IntegerField(
        label=_(u"Organization of general contractor"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-organization',
                args=[GENERAL_CONTRACTOR_ORGA.pk]),
            associated_model=Organization),
        validators=[valid_id(Organization)])
    associated_file__numeric_reference = forms.IntegerField(
        label=_("File numeric reference"))
    associated_file__year = forms.IntegerField(label=_("File year"))
    associated_file__internal_reference = forms.CharField(
        max_length=200, label=_("File other reference"))
    associated_file__in_charge = forms.IntegerField(
        label=_(u"File in charge"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=[SRA_AGENT.pk]),
            associated_model=Person),
        validators=[valid_id(Person)])
    associated_file__permit_reference = forms.CharField(
        max_length=200, label=_("File permit reference"))
    history_creator = forms.IntegerField(
        label=_(u"Created by"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person',
                args=['0', 'user']),
            associated_model=Person),
        validators=[valid_id(Person)])
    history_modifier = forms.IntegerField(
        label=_(u"Modified by"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=['0', 'user']),
            associated_model=Person),
        validators=[valid_id(Person)])

    def __init__(self, *args, **kwargs):
        super(AdministrativeActFileSelect, self).__init__(*args, **kwargs)
        self.fields['act_type'].choices = ActType.get_types(
            dct={'intented_to': 'F'})
        self.fields['act_type'].help_text = ActType.get_help(
            dct={'intented_to': 'F'})
        if settings.ISHTAR_DPTS:
            k = 'associated_file__towns__numero_insee__startswith'
            self.fields[k].choices = [
                ('', '--')] + list(settings.ISHTAR_DPTS)

    def get_input_ids(self):
        ids = super(AdministrativeActFileSelect, self).get_input_ids()
        ids.pop(ids.index('parcel'))
        ids.append('parcel_0')
        ids.append('parcel_1')
        return ids


class AdministrativeActFileFormSelection(AdministrativeActOpeFormSelection):
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-administrativeactfile'),
            AdministrativeActFileSelect, AdministrativeAct,
            table_cols='TABLE_COLS_FILE'),
        validators=[valid_id(AdministrativeAct)])


class AdministrativeActFileModifyFormSelection(
        AdministrativeActOpeFormSelection):
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-administrativeactfile'),
            AdministrativeActFileModifySelect, AdministrativeAct,
            table_cols='TABLE_COLS_FILE'),
        validators=[valid_id(AdministrativeAct)])


class AdministrativeActFileForm(AdministrativeActOpeForm):
    act_type = forms.ChoiceField(label=_(u"Act type"), choices=[])

    def __init__(self, *args, **kwargs):
        super(AdministrativeActFileForm, self).__init__(*args, **kwargs)
        self.fields['act_type'].choices = ActType.get_types(
            dct={'intented_to': 'F'})
        self.fields['act_type'].help_text = ActType.get_help(
            dct={'intented_to': 'F'})
