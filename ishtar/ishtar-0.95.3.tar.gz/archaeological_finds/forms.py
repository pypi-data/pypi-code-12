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
Finds forms definitions
"""

from django import forms
from django.conf import settings
from django.core import validators
from django.core.exceptions import PermissionDenied
from django.forms.formsets import formset_factory
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from ishtar_common.models import Person, valid_id, valid_ids
from archaeological_operations.models import Period, ArchaeologicalSite
from archaeological_context_records.models import DatingType, DatingQuality, \
    ContextRecord
from archaeological_warehouse.models import Warehouse
import models

from ishtar_common import widgets
from ishtar_common.forms import FormSet, FloatField, \
    get_form_selection, reverse_lazy, TableSelect, get_now, FinalForm
from ishtar_common.forms_common import get_town_field, SourceSelect


class RecordFormSelection(forms.Form):
    form_label = _("Context record")
    base_models = ['get_first_base_find']
    associated_models = {'get_first_base_find__context_record': ContextRecord}
    get_first_base_find__context_record = forms.IntegerField(
        label=_(u"Context record"), required=False,
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-contextrecord'),
            associated_model=ContextRecord),
        validators=[valid_id(ContextRecord)])

    def __init__(self, *args, **kwargs):
        super(RecordFormSelection, self).__init__(*args, **kwargs)
        # get the current operation and restrict search to it
        cr_pk = None
        if 'data' in kwargs and kwargs['data']:
            cr_pk = kwargs['data'].get(
                'get_first_base_find__context_record')
        if not cr_pk and 'initial' in kwargs and kwargs['initial']:
            cr_pk = kwargs['initial'].get(
                'get_first_base_find__context_record')
        if not cr_pk:
            return
        try:
            cr = ContextRecord.objects.get(pk=cr_pk)
        except ContextRecord.DoesNotExist:
            return
        widget = self.fields['get_first_base_find__context_record'].widget
        widget.source = unicode(widget.source) + "?operation__pk={}".format(
            cr.operation.pk)


class FindForm(forms.Form):
    file_upload = True
    form_label = _("Find")
    base_models = ['get_first_base_find', 'object_type', 'material_type',
                   'preservation_to_consider', 'integritie']
    associated_models = {'material_type': models.MaterialType,
                         'conservatory_state': models.ConservatoryState,
                         'object_type': models.ObjectType,
                         'preservation_to_consider': models.PreservationType,
                         'integritie': models.IntegrityType}
    label = forms.CharField(
        label=_(u"Free ID"),
        validators=[validators.MaxLengthValidator(60)])
    previous_id = forms.CharField(label=_("Previous ID"), required=False)
    description = forms.CharField(label=_("Description"),
                                  widget=forms.Textarea, required=False)
    get_first_base_find__batch = forms.ChoiceField(
        label=_(u"Batch/object"), choices=models.IS_ISOLATED_CHOICES,
        required=False)
    is_complete = forms.NullBooleanField(label=_(u"Is complete?"),
                                         required=False)
    material_type = widgets.MultipleAutocompleteField(
        model=models.MaterialType, label=_(u"Material type"), required=False)
    conservatory_state = forms.ChoiceField(label=_(u"Conservatory state"),
                                           choices=[], required=False)
    object_type = widgets.MultipleAutocompleteField(
        model=models.ObjectType, label=_(u"Object types"), required=False)
    preservation_to_consider = forms.MultipleChoiceField(
        label=_(u"Preservation type"), choices=[],
        widget=forms.CheckboxSelectMultiple, required=False)
    integritie = forms.MultipleChoiceField(
        label=_(u"Integrity"), choices=[],
        widget=forms.CheckboxSelectMultiple, required=False)
    length = FloatField(label=_(u"Length (cm)"), required=False)
    width = FloatField(label=_(u"Width (cm)"), required=False)
    height = FloatField(label=_(u"Height (cm)"), required=False)
    diameter = FloatField(label=_(u"Diameter (cm)"), required=False)
    volume = FloatField(label=_(u"Volume (l)"), required=False)
    weight = FloatField(label=_(u"Weight (g)"), required=False)
    find_number = forms.IntegerField(label=_(u"Find number"), required=False)
    mark = forms.CharField(label=_(u"Mark"), required=False)
    checked = forms.ChoiceField(label=_(u"Check"))
    check_date = forms.DateField(
        initial=get_now, label=_(u"Check date"), widget=widgets.JQueryDate)
    comment = forms.CharField(label=_(u"Comment"), required=False,
                              widget=forms.Textarea)
    dating_comment = forms.CharField(
        label=_(u"Comment on dating"), required=False, widget=forms.Textarea)
    image = forms.ImageField(
        label=_(u"Image"), help_text=mark_safe(
            _(u"<p>Heavy images are resized to: %(width)dx%(height)d "
              u"(ratio is preserved).</p>") % {
                'width': settings.IMAGE_MAX_SIZE[0],
                'height': settings.IMAGE_MAX_SIZE[1]}),
        required=False, widget=widgets.ImageFileInput())

    def __init__(self, *args, **kwargs):
        super(FindForm, self).__init__(*args, **kwargs)
        self.fields['checked'].choices = models.CHECK_CHOICES
        self.fields['material_type'].choices = models.MaterialType.get_types()
        self.fields['material_type'].help_text = models.MaterialType.get_help()
        self.fields['conservatory_state'].choices = \
            models.ConservatoryState.get_types()
        self.fields['conservatory_state'].help_text = \
            models.ConservatoryState.get_help()
        self.fields['preservation_to_consider'].choices = \
            models.PreservationType.get_types(empty_first=False)
        self.fields['preservation_to_consider'].help_text = \
            models.PreservationType.get_help()
        self.fields['integritie'].choices = \
            models.IntegrityType.get_types(empty_first=False)
        self.fields['integritie'].help_text = \
            models.IntegrityType.get_help()


class DateForm(forms.Form):
    form_label = _("Dating")
    base_model = 'dating'
    associated_models = {'dating_type': DatingType,
                         'quality': DatingQuality,
                         'period': Period}
    period = forms.ChoiceField(label=_("Period"), choices=[])
    start_date = forms.IntegerField(label=_(u"Start date"),
                                    required=False)
    end_date = forms.IntegerField(label=_(u"End date"), required=False)
    quality = forms.ChoiceField(label=_("Quality"), required=False,
                                choices=[])
    dating_type = forms.ChoiceField(label=_("Dating type"),
                                    required=False, choices=[])
    precise_dating = forms.CharField(label=_("Precise dating"),
                                     required=False)

    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs)
        self.fields['dating_type'].choices = DatingType.get_types()
        self.fields['dating_type'].help_text = DatingType.get_help()
        self.fields['period'].choices = Period.get_types()
        self.fields['period'].help_text = Period.get_help()
        self.fields['quality'].choices = DatingQuality.get_types()
        self.fields['quality'].help_text = DatingQuality.get_help()


DatingFormSet = formset_factory(DateForm, can_delete=True,
                                formset=FormSet)
DatingFormSet.form_label = _("Dating")


class FindSelect(TableSelect):
    base_finds__cache_short_id = forms.CharField(label=_(u"Short ID"))
    base_finds__cache_complete_id = forms.CharField(label=_(u"Complete ID"))
    label = forms.CharField(label=_(u"Free ID"))
    base_finds__context_record__parcel__town = get_town_field()
    base_finds__context_record__operation__year = forms.IntegerField(
        label=_(u"Year"))
    base_finds__context_record__operation__code_patriarche = \
        forms.IntegerField(label=_(u"Code PATRIARCHE"))
    archaeological_sites = forms.IntegerField(
        label=_("Archaelogical site"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-archaeologicalsite'),
            associated_model=ArchaeologicalSite),
        validators=[valid_id(ArchaeologicalSite)])
    datings__period = forms.ChoiceField(label=_(u"Period"), choices=[])
    # TODO search by warehouse
    material_types = forms.ChoiceField(label=_(u"Material type"), choices=[])
    object_types = forms.ChoiceField(label=_(u"Object type"), choices=[])
    preservation_to_considers = forms.ChoiceField(
        choices=[], label=_(u"Preservation type"))
    conservatory_state = forms.ChoiceField(label=_(u"Conservatory state"),
                                           choices=[])
    integrities = forms.ChoiceField(label=_(u"Integrity"), choices=[])
    base_finds__find__description = forms.CharField(label=_(u"Description"))
    base_finds__batch = forms.ChoiceField(
        label=_(u"Batch/object"),
        choices=[('', '--')] + list(models.IS_ISOLATED_CHOICES))
    checked = forms.ChoiceField(label=_("Check"))
    image = forms.NullBooleanField(label=_(u"Has an image?"))

    def __init__(self, *args, **kwargs):
        super(FindSelect, self).__init__(*args, **kwargs)
        self.fields['datings__period'].choices = Period.get_types()
        self.fields['datings__period'].help_text = Period.get_help()
        self.fields['material_types'].choices = \
            models.MaterialType.get_types()
        self.fields['material_types'].help_text = \
            models.MaterialType.get_help()
        self.fields['conservatory_state'].choices = \
            models.ConservatoryState.get_types()
        self.fields['conservatory_state'].help_text = \
            models.ConservatoryState.get_help()
        self.fields['object_types'].choices = \
            models.ObjectType.get_types()
        self.fields['checked'].choices = \
            [('', '--')] + list(models.CHECK_CHOICES)
        self.fields['preservation_to_considers'].choices = \
            models.PreservationType.get_types()
        self.fields['preservation_to_considers'].help_text = \
            models.PreservationType.get_help()
        self.fields['integrities'].choices = \
            models.IntegrityType.get_types()
        self.fields['integrities'].help_text = \
            models.IntegrityType.get_help()


class FindFormSelection(forms.Form):
    form_label = _("Find search")
    associated_models = {'pk': models.Find}
    currents = {'pk': models.Find}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-find'),
            FindSelect, models.Find,
            source_full=reverse_lazy('get-find-full')),
        validators=[valid_id(models.Find)])


class MultipleFindFormSelection(forms.Form):
    form_label = _("Find search")
    associated_models = {'pk': models.Find}
    currents = {'pk': models.Find}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-find'),
            FindSelect, models.Find,
            multiple_select=True,
            source_full=reverse_lazy('get-find-full')),
        validators=[valid_id(models.Find)])


class BaseTreatmentForm(forms.Form):
    form_label = _(u"Base treatment")
    associated_models = {'treatment_type': models.TreatmentType,
                         'person': Person,
                         'location': Warehouse}
    treatment_type = forms.ChoiceField(label=_(u"Treatment type"), choices=[])
    person = forms.IntegerField(
        label=_(u"Person"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person'), associated_model=Person,
            new=True),
        validators=[valid_id(Person)])
    location = forms.IntegerField(
        label=_(u"Location"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-warehouse'), associated_model=Warehouse,
            new=True),
        validators=[valid_id(Warehouse)])
    description = forms.CharField(label=_(u"Description"),
                                  widget=forms.Textarea, required=False)
    start_date = forms.DateField(label=_(u"Start date"), required=False,
                                 widget=widgets.JQueryDate)
    end_date = forms.DateField(label=_(u"End date"), required=False,
                               widget=widgets.JQueryDate)

    def __init__(self, *args, **kwargs):
        super(BaseTreatmentForm, self).__init__(*args, **kwargs)
        self.fields['treatment_type'].choices = models.TreatmentType.get_types(
            exclude=['packaging'])
        self.fields['treatment_type'].help_text = \
            models.TreatmentType.get_help(exclude=['packaging'])


class FindMultipleFormSelection(forms.Form):
    form_label = _(u"Upstream finds")
    associated_models = {'finds': models.Find}
    associated_labels = {'finds': _(u"Finds")}
    finds = forms.CharField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-find'), FindSelect, models.Find, multiple=True,
            multiple_cols=[2, 3, 4]),
        validators=[valid_ids(models.Find)])

    def clean(self):
        if 'finds' not in self.cleaned_data or not self.cleaned_data['finds']:
            raise forms.ValidationError(_(u"You should at least select one "
                                          u"archaeological find."))
        return self.cleaned_data


def check_treatment(form_name, type_key, type_list=[], not_type_list=[]):
    type_list = [models.TreatmentType.objects.get(txt_idx=tpe).pk
                 for tpe in type_list]
    not_type_list = [models.TreatmentType.objects.get(txt_idx=tpe).pk
                     for tpe in not_type_list]

    def func(self, request, storage):
        if storage.prefix not in request.session or \
           'step_data' not in request.session[storage.prefix] or \
           form_name not in request.session[storage.prefix]['step_data'] or\
           form_name + '-' + type_key not in \
           request.session[storage.prefix]['step_data'][form_name]:
            return False
        try:
            type = int(request.session[storage.prefix]['step_data']
                                      [form_name][form_name + '-' + type_key])
            return (not type_list or type in type_list) \
                and type not in not_type_list
        except ValueError:
            return False
    return func


class ResultFindForm(forms.Form):
    form_label = _(u"Resulting find")
    associated_models = {'material_type': models.MaterialType}
    label = forms.CharField(
        label=_(u"Free ID"),
        validators=[validators.MaxLengthValidator(60)])
    description = forms.CharField(label=_(u"Precise description"),
                                  widget=forms.Textarea)
    material_type = forms.ChoiceField(label=_(u"Material type"), choices=[])
    volume = forms.IntegerField(label=_(u"Volume (l)"))
    weight = forms.IntegerField(label=_(u"Weight (g)"))
    find_number = forms.IntegerField(label=_(u"Find number"))

    def __init__(self, *args, **kwargs):
        super(ResultFindForm, self).__init__(*args, **kwargs)
        self.fields['material_type'].choices = models.MaterialType.get_types()
        self.fields['material_type'].help_text = models.MaterialType.get_help()

ResultFindFormSet = formset_factory(ResultFindForm, can_delete=True,
                                    formset=FormSet)
ResultFindFormSet.form_label = _(u"Resulting finds")


class FindDeletionForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to delete this find?")


class UpstreamFindFormSelection(FindFormSelection):
    form_label = _(u"Upstream find")

#############################################
# Source management for archaelogical finds #
#############################################

SourceFindFormSelection = get_form_selection(
    'SourceFindFormSelection', _(u"Archaeological find search"), 'find',
    models.Find, FindSelect, 'get-find',
    _(u"You should select an archaeological find."))


class FindSourceSelect(SourceSelect):
    find__base_finds__context_record__operation__year = forms.IntegerField(
        label=_(u"Year of the operation"))
    find__datings__period = forms.ChoiceField(
        label=_(u"Period of the archaelogical find"), choices=[])
    find__material_type = forms.ChoiceField(
        label=_("Material type of the archaelogical find"), choices=[])
    find__description = forms.CharField(
        label=_(u"Description of the archaelogical find"))

    def __init__(self, *args, **kwargs):
        super(FindSourceSelect, self).__init__(*args, **kwargs)
        self.fields['find__datings__period'].choices = Period.get_types()
        self.fields['find__datings__period'].help_text = Period.get_help()
        self.fields['find__material_type'].choices = \
            models.MaterialType.get_types()
        self.fields['find__material_type'].help_text = \
            models.MaterialType.get_help()

FindSourceFormSelection = get_form_selection(
    'FindSourceFormSelection', _(u"Documentation search"), 'pk',
    models.FindSource, FindSourceSelect, 'get-findsource',
    _(u"You should select a document."),
    get_full_url='get-findsource-full')


class NewFindBasketForm(forms.ModelForm):
    class Meta:
        model = models.FindBasket
        fields = ('label', 'comment')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(NewFindBasketForm, self).__init__(*args, **kwargs)

    def clean(self):
        q = models.FindBasket.objects.filter(user=self.user,
                                             label=self.cleaned_data['label'])
        if q.count():
            raise forms.ValidationError(_(u"Another basket already exist with "
                                          u"this name."))
        return self.cleaned_data

    def save(self, commit=True):
        self.instance.user = self.user
        return super(NewFindBasketForm, self).save(commit)


class SelectFindBasketForm(forms.Form):
    basket = forms.ChoiceField(label=_(u"Basket"), required=True, choices=[])

    def __init__(self, *args, **kwargs):
        self.user = None
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(SelectFindBasketForm, self).__init__(*args, **kwargs)
        if not self.user:
            return
        self.fields['basket'].choices = [('', '--')] + [
            (b.pk, unicode(b))
            for b in models.FindBasket.objects.filter(user=self.user)]


class DeleteFindBasketForm(SelectFindBasketForm):
    def save(self):
        try:
            models.FindBasket.objects.get(pk=self.cleaned_data['basket'],
                                          user=self.user).delete()
        except models.FindBasket.DoesNotExist:
            # something strange... TODO: log it
            pass
        return


class FindBasketAddItemForm(forms.Form):
    basket_id = forms.IntegerField(required=True)
    item_id = forms.IntegerField(required=True)

    def save(self, user):
        try:
            basket = models.FindBasket.objects.get(
                pk=self.cleaned_data['basket_id'], user=user.ishtaruser)
            item = models.Find.objects.get(
                pk=self.cleaned_data['item_id'])
        except models.FindBasket.DoesNotExist or\
                models.Find.DoesNotExist:
            # something strange... TODO: log it
            raise PermissionDenied
        # check rights
        if not user.is_superuser and \
                not user.ishtaruser.has_right('change_find') and \
                not (user.ishtaruser.has_right('change_own_find')
                     and item.is_own(user)):
            raise PermissionDenied
        basket.items.add(item)
        return basket

"""
####################################
# Source management for treatments #
####################################

SourceTreatementFormSelection = get_form_selection(
    'SourceTreatmentFormSelection', _(u"Treatment search"), 'operation',
    models.Treatment, TreatmentSelect, 'get-treatment',
    _(u"You should select a treatment."))

class TreatmentSourceSelect(SourceSelect):
    operation__towns = get_town_field(label=_(u"Operation's town"))
    treatment__treatment_type = forms.ChoiceField(label=_(u"Operation type"),
                                                  choices=[])
    operation__year = forms.IntegerField(label=_(u"Operation's year"))

    def __init__(self, *args, **kwargs):
        super(OperationSourceSelect, self).__init__(*args, **kwargs)
        self.fields['operation__operation_type'].choices = \
                                                 OperationType.get_types()
        self.fields['operation__operation_type'].help_text = \
                                                 OperationType.get_help()

"""

"""
OperationSourceFormSelection = get_form_selection(
    'OperationSourceFormSelection', _(u"Documentation search"), 'pk',
    models.OperationSource, OperationSourceSelect, 'get-operationsource',
    _(u"You should select a document."))

operation_source_modification_wizard = OperationSourceWizard([
         ('selec-operation_source_modification', OperationSourceFormSelection),
         ('source-operation_source_modification', SourceForm),
         ('authors-operation_source_modification', AuthorFormset),
         ('final-operation_source_modification', FinalForm)],
          url_name='operation_source_modification',)

class OperationSourceDeletionWizard(DeletionWizard):
    model = models.OperationSource
    fields = ['operation', 'title', 'source_type', 'authors',]

operation_source_deletion_wizard = OperationSourceDeletionWizard([
         ('selec-operation_source_deletion', OperationSourceFormSelection),
         ('final-operation_source_deletion', SourceDeletionForm)],
          url_name='operation_source_deletion',)
"""
