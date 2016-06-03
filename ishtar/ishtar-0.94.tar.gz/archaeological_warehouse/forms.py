#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2013  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ishtar_common.models import Person, valid_id
from archaeological_finds.models import TreatmentType
import models
from ishtar_common import widgets
from ishtar_common.forms import name_validator, reverse_lazy, \
    get_form_selection, TableSelect
from archaeological_finds.forms import FindMultipleFormSelection


def get_warehouse_field(label=_(u"Warehouse"), required=True):
    # !FIXME hard_link, reverse_lazy doen't seem to work with formsets
    url = "/" + settings.URL_PATH + 'autocomplete-warehouse'
    widget = widgets.JQueryAutoComplete(url, associated_model=models.Warehouse)
    return forms.IntegerField(widget=widget, label=label, required=required,
                              validators=[valid_id(models.Warehouse)])


class WarehouseForm(forms.Form):
    name = forms.CharField(label=_(u"Name"), max_length=40,
                           validators=[name_validator])
    warehouse_type = forms.ChoiceField(label=_(u"Warehouse type"),
                                       choices=[])
    person_in_charge = forms.IntegerField(
        label=_(u"Person in charge"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person'),
            associated_model=models.Person),
        validators=[valid_id(models.Person)],
        required=False)
    comment = forms.CharField(label=_(u"Comment"), widget=forms.Textarea,
                              required=False)
    address = forms.CharField(label=_(u"Address"), widget=forms.Textarea,
                              required=False)
    address_complement = forms.CharField(label=_(u"Address complement"),
                                         widget=forms.Textarea, required=False)
    postal_code = forms.CharField(label=_(u"Postal code"), max_length=10,
                                  required=False)
    town = forms.CharField(label=_(u"Town"), max_length=30, required=False)
    country = forms.CharField(label=_(u"Country"), max_length=30,
                              required=False)
    phone = forms.CharField(label=_(u"Phone"), max_length=18, required=False)
    mobile_phone = forms.CharField(label=_(u"Town"), max_length=18,
                                   required=False)

    def __init__(self, *args, **kwargs):
        super(WarehouseForm, self).__init__(*args, **kwargs)
        self.fields['warehouse_type'].choices = \
            models.WarehouseType.get_types()
        self.fields['warehouse_type'].help_text = \
            models.WarehouseType.get_help()

    def save(self, user):
        dct = self.cleaned_data
        dct['history_modifier'] = user
        dct['warehouse_type'] = models.WarehouseType.objects.get(
            pk=dct['warehouse_type'])
        if 'person_in_charge' in dct and dct['person_in_charge']:
            dct['person_in_charge'] = models.Person.objects.get(
                pk=dct['person_in_charge'])
        new_item = models.Warehouse(**dct)
        new_item.save()
        return new_item


class ContainerForm(forms.Form):
    form_label = _(u"Container")
    reference = forms.CharField(label=_(u"Ref."))
    container_type = forms.ChoiceField(label=_(u"Container type"), choices=[])
    location = forms.IntegerField(
        label=_(u"Warehouse"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-warehouse'),
            associated_model=models.Warehouse, new=True),
        validators=[valid_id(models.Warehouse)])
    comment = forms.CharField(label=_(u"Comment"),
                              widget=forms.Textarea, required=False)

    def __init__(self, *args, **kwargs):
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['container_type'].choices = \
            models.ContainerType.get_types()
        self.fields['container_type'].help_text = \
            models.ContainerType.get_help()

    def save(self, user):
        dct = self.cleaned_data
        dct['history_modifier'] = user
        dct['container_type'] = models.ContainerType.objects.get(
            pk=dct['container_type'])
        dct['location'] = models.Warehouse.objects.get(pk=dct['location'])
        new_item = models.Container(**dct)
        new_item.save()
        return new_item


class ContainerSelect(TableSelect):
    location = get_warehouse_field()
    container_type = forms.ChoiceField(label=_(u"Container type"), choices=[])
    reference = forms.CharField(label=_(u"Ref."))

    def __init__(self, *args, **kwargs):
        super(ContainerSelect, self).__init__(*args, **kwargs)
        self.fields['container_type'].choices = \
            models.ContainerType.get_types()
        self.fields['container_type'].help_text = \
            models.ContainerType.get_help()

ContainerFormSelection = get_form_selection(
    'ContainerFormSelection', _(u"Container search"), 'container',
    models.Container, ContainerSelect, 'get-container',
    _(u"You should select a container."), new=True,
    new_message=_(u"Add a new container"))


class BasePackagingForm(forms.Form):
    form_label = _(u"Packaging")
    associated_models = {'treatment_type': TreatmentType,
                         'person': Person,
                         'location': models.Warehouse}
    treatment_type = forms.IntegerField(label="", widget=forms.HiddenInput)
    person = forms.IntegerField(
        label=_(u"Packager"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person'),
            associated_model=Person, new=True),
        validators=[valid_id(Person)])
    start_date = forms.DateField(
        label=_(u"Date"), required=False, widget=widgets.JQueryDate)

    def __init__(self, *args, **kwargs):
        super(BasePackagingForm, self).__init__(*args, **kwargs)
        self.fields['treatment_type'].initial = \
            TreatmentType.objects.get(txt_idx='packaging').pk


class FindPackagingFormSelection(FindMultipleFormSelection):
    form_label = _(u"Packaged finds")
