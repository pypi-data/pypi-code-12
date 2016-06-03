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
Forms definition
"""
import datetime
import re

from django import forms
from django.core.urlresolvers import reverse
from django.core import validators
from django.forms.formsets import BaseFormSet, DELETION_FIELD_NAME
from django.utils import formats
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

# from formwizard.forms import NamedUrlSessionFormWizard


class NamedUrlSessionFormWizard(forms.Form):
    def __init__(self, form_list, condition_list={}, url_name=''):
        self.form_list = dict(form_list)
        self.condition_list = condition_list
        self.url_name = url_name
        super(NamedUrlSessionFormWizard, self).__init__(self)

    def rindex(self, idx):
        return self.url_name.rindex(idx)

import models
import widgets

reverse_lazy = lazy(reverse, unicode)

regexp_name = re.compile(r"^[,:/\w\-'\"() \&\[\]@]+$", re.UNICODE)
name_validator = validators.RegexValidator(
    regexp_name,
    _(u"Enter a valid name consisting of letters, spaces and hyphens."),
    'invalid')


class FloatField(forms.FloatField):
    """
    Allow the use of comma for separating float fields
    """
    def clean(self, value):
        if value:
            value = value.replace(',', '.').replace('%', '')
        return super(FloatField, self).clean(value)


class FinalForm(forms.Form):
    final = True
    form_label = _(u"Confirm")


class FinalDeleteForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Are you sure you want to delete?")


class FormSet(BaseFormSet):
    def check_duplicate(self, key_names, error_msg=""):
        """Check for duplicate items in the formset"""
        if any(self.errors):
            return
        if not error_msg:
            error_msg = _("There are identical items.")
        items = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if not form.is_valid():
                continue
            item = [key_name in form.cleaned_data and
                    form.cleaned_data[key_name]
                    for key_name in key_names]
            if not [v for v in item if v]:
                continue
            if item in items:
                raise forms.ValidationError, error_msg
            items.append(item)

    def add_fields(self, form, index):
        super(FormSet, self).add_fields(form, index)
        form.fields[DELETION_FIELD_NAME].label = ''
        form.fields[DELETION_FIELD_NAME].widget = widgets.DeleteWidget()


class TableSelect(forms.Form):
    def __init__(self, *args, **kwargs):
        super(TableSelect, self).__init__(*args, **kwargs)
        key = self.fields.keyOrder[0]
        self.fields[key].widget.attrs['autofocus'] = 'autofocus'

    def get_input_ids(self):
        return self.fields.keys()


def get_now():
    format = formats.get_format('DATE_INPUT_FORMATS')[0]
    value = datetime.datetime.now().strftime(format)
    return value


class ClosingDateFormSelection(forms.Form):
    form_label = _("Closing date")
    end_date = forms.DateField(label=_(u"Closing date"),
                               widget=widgets.JQueryDate)


def get_form_selection(
        class_name, label, key, model, base_form, get_url,
        not_selected_error=_(u"You should select an item."), new=False,
        new_message=_(u"Add a new item"), get_full_url=None):
    """
    Generate a class selection form
        class_name -- name of the class
        label -- label of the form
        key -- model,
        base_form -- base form to select
        get_url -- url to get the item
        not_selected_error -- message displayed when no item is selected
        new -- can add new items
        new_message -- message of link to add new items
    """
    attrs = {'_main_key': key,
             '_not_selected_error': not_selected_error,
             'form_label': label,
             'associated_models': {key: model},
             'currents': {key: model}}
    widget_kwargs = {"new": new, "new_message": new_message}
    if get_full_url:
        widget_kwargs['source_full'] = reverse_lazy(get_full_url)
    attrs[key] = forms.IntegerField(
        label="", required=False,
        validators=[models.valid_id(model)],
        widget=widgets.JQueryJqGrid(reverse_lazy(get_url), base_form, model,
                                    **widget_kwargs))

    def clean(self):
        cleaned_data = self.cleaned_data
        if self._main_key not in cleaned_data \
           or not cleaned_data[self._main_key]:
            raise forms.ValidationError(self._not_selected_error)
        return cleaned_data
    attrs['clean'] = clean
    return type(class_name, (forms.Form,), attrs)


class DocumentGenerationForm(forms.Form):
    """
    Form to generate document by choosing the template
    """
    _associated_model = None  # ex: AdministrativeAct
    # ex: 'archaeological_operations.models.AdministrativeAct'
    _associated_object_name = ''
    document_template = forms.ChoiceField(label=_("Template"), choices=[])

    def __init__(self, *args, **kwargs):
        super(DocumentGenerationForm, self).__init__(*args, **kwargs)
        self.fields['document_template'].choices = \
            models.DocumentTemplate.get_tuples(
                dct={'associated_object_name': self._associated_object_name})

    def save(self, object_pk):
        try:
            c_object = self._associated_model.objects.get(pk=object_pk)
        except self._associated_model.DoesNotExist:
            return
        try:
            template = models.DocumentTemplate.objects.get(
                pk=self.cleaned_data.get('document_template'))
        except models.DocumentTemplate.DoesNotExist:
            return
        return template.publish(c_object)
