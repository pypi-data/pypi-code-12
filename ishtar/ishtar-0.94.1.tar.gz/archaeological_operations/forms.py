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
Operations forms definitions
"""
import datetime
from itertools import groupby

from django import forms
from django.conf import settings
from django.core import validators
from django.db.models import Max

from django.forms.formsets import formset_factory, DELETION_FIELD_NAME, \
    TOTAL_FORM_COUNT
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.utils.safestring import mark_safe

from ishtar_common.models import valid_id, PersonType, Person, Town, \
    DocumentTemplate, Organization, OrganizationType, get_current_profile

from ishtar_common.wizards import MultiValueDict

from archaeological_files.models import File
import models

from widgets import ParcelWidget, SelectParcelWidget
from ishtar_common import widgets

from ishtar_common.forms import FinalForm, FormSet, get_now, \
    reverse_lazy, get_form_selection, TableSelect
from ishtar_common.forms_common import TownFormSet, SourceForm, SourceSelect, \
    get_town_field

from archaeological_operations.utils import parse_parcels


class ParcelField(forms.MultiValueField):
    def __init__(self, *args, **kwargs):
        if 'widget' not in kwargs:
            self.widget = ParcelWidget()
        return super(ParcelField, self).__init__(*args, **kwargs)

    def compress(data_list):
        return u"-".join(data_list)


class ParcelForm(forms.Form):
    form_label = _("Parcels")
    base_model = 'parcel'
    associated_models = {'parcel': models.Parcel, 'town': models.Town, }
    town = forms.ChoiceField(label=_("Town"), choices=(), required=False,
                             validators=[valid_id(models.Town)])
    year = forms.IntegerField(label=_("Year"), required=False,
                              validators=[validators.MinValueValidator(1900),
                                          validators.MaxValueValidator(2100)])
    section = forms.CharField(label=_(u"Section"), required=False,
                              validators=[validators.MaxLengthValidator(4)])
    parcel_number = forms.CharField(
        label=_(u"Parcel number"), required=False,
        validators=[validators.MaxLengthValidator(6)])

    def __init__(self, *args, **kwargs):
        towns = None
        if 'data' in kwargs and 'TOWNS' in kwargs['data']:
            towns = kwargs['data']['TOWNS']
            # clean data if not "real" data
            prefix_value = kwargs['prefix'] + '-town'
            if not [k for k in kwargs['data'].keys()
                    if k.startswith(prefix_value) and kwargs['data'][k]]:
                kwargs['data'] = None
                if 'files' in kwargs:
                    kwargs.pop('files')
        super(ParcelForm, self).__init__(*args, **kwargs)
        if towns:
            self.fields['town'].choices = towns

    def clean(self):
        """Check required fields"""
        if any(self.errors):
            return
        if not self.cleaned_data or (DELETION_FIELD_NAME in self.cleaned_data
           and self.cleaned_data[DELETION_FIELD_NAME]):
            return
        if not self.cleaned_data.get('parcel_number') and \
           self.cleaned_data.get('section') != 'DP':
            return {}
        for key in ('town', 'section'):
            if key not in self.cleaned_data or not self.cleaned_data[key]:
                raise forms.ValidationError(_(u"Town section and parcel number"
                                              u" fields are required."))
        return self.cleaned_data

    @classmethod
    def get_formated_datas(cls, cleaned_datas):
        result, current, deleted = [], [], []
        towns = {}
        for data in cleaned_datas:
            if not data:
                continue
            town = data.get('town') or ''
            if town:
                if town in towns:
                    town = towns[town]
                else:
                    try:
                        towns[town] = unicode(Town.objects.get(pk=town))
                        town = towns[town]
                    except (Town.DoesNotExist, ValueError):
                        town = ''
            parcel_number = data.get('parcel_number') or ''
            c_number = 0
            if parcel_number:
                parcel_nb = list(reversed(list(parcel_number)))
                c_number = ''
                while parcel_nb:
                    c = parcel_nb.pop()
                    try:
                        c_number += str(int(c))
                    except ValueError:
                        break
                if c_number:
                    c_number = int(c_number)
                else:
                    c_number = 0
            values = [town, data.get('year') or '', data.get('section') or '',
                      c_number, data.get('parcel_number') or '']
            if data.get('DELETE'):
                deleted.append(values)
            else:
                current.append(values)
        if current:
            result.append((_("Current parcels"), cls._format_parcels(current)))
        if deleted:
            result.append((_("Deleted parcels"), cls._format_parcels(deleted)))
        return result

    @classmethod
    def _format_parcels(cls, parcels):
        sortkeyfn = lambda s: (s[0], s[1], s[2])
        parcels = sorted(parcels, key=sortkeyfn)
        grouped = []
        for keys, parcel_grp in groupby(parcels, key=sortkeyfn):
            keys = list(keys)
            keys.append([gp[-1] for gp in parcel_grp])
            grouped.append(keys)
        res = ''
        c_town, c_section = '', ''
        for idx, parcel in enumerate(grouped):
            town, year, section, parcel_numbers = parcel
            if c_town != town:
                c_town = town
                c_section = ''
                if idx:
                    res += " ; "
                res += town + u' : '
            if c_section:
                res += u" / "
            c_section = section
            res += section + u' '
            res += u", ".join(parcel_numbers)
            if year:
                res += " (%s)" % unicode(year)
        return res


class ParcelSelectionForm(forms.Form):
    _town = forms.ChoiceField(label=_("Town"), choices=(), required=False,
                              validators=[valid_id(models.Town)])
    _parcel_selection = forms.CharField(
        label=_(u"Full text input"),
        widget=SelectParcelWidget(attrs={'class': 'parcel-select'}),
        help_text=_(u"example: \"2013: XD:1 to 13,24,33 to 39, YD:24\" or "
                    u"\"AB:24,AC:42\""),
        max_length=100, required=False)


class ParcelFormSet(FormSet):
    SELECTION_FORM = ParcelSelectionForm

    def __init__(self, *args, **kwargs):
        if 'data' in kwargs and kwargs['data']:
            kwargs['data'] = self.rearrange_parcels(kwargs['data'])
        super(FormSet, self).__init__(*args, **kwargs)
        self.extra_form = None
        if self.forms[0].__class__.__name__ == 'ParcelForm':
            self.selection_form = ParcelSelectionForm()
            self.extra_form = self.selection_form
            # copy town choices
            town_choices = self.forms[0].fields['town'].choices[:]
            if town_choices and not town_choices[0][0]:
                # remove empty
                town_choices = town_choices[1:]
            if town_choices:
                self.selection_form.fields['_town'].choices = town_choices

    def rearrange_parcels(self, parcels):
        """
        Simple database ordering is not possible as a numeric ordering of
        parcel number have to be made but with parcel number not strictly
        numeric
        Very complicated for a simple thing :(
        """
        prefix, ordering_keys, values = '', {}, {}
        new_values = MultiValueDict()
        for k in parcels:
            value = parcels[k]
            splitted = k.split('-')
            if len(splitted) < 4:
                new_values[k] = value
                continue
            if not prefix:
                prefix = "-".join(splitted[:-2])
            field = splitted[-1]
            number = splitted[-2]

            if number not in values:
                values[number] = {}
            values[number][field] = value

            if field == 'parcel':
                if not value:
                    continue
                try:
                    parcel = models.Parcel.objects.get(pk=value)
                except models.Parcel.DoesNotExist:
                    continue
                ordering_keys[number] = [
                    parcel.town, parcel.year, parcel.section,
                    parcel.parcel_number]
                continue
            if number not in ordering_keys:
                ordering_keys[number] = ['', '', '', '']
            if field == 'town':
                ordering_keys[number][0] = value
            elif field == 'year':
                ordering_keys[number][1] = value
            elif field == 'section':
                ordering_keys[number][2] = value
            elif field == 'parcel_number':
                ordering_keys[number][3] = value

        reverse_ordering_keys = {}
        for number in ordering_keys:
            reverse_ordering_keys[tuple(ordering_keys[number])] = number

        for new_idx, keys in enumerate(sorted(reverse_ordering_keys.keys(),
                                       key=self._parcel_sorting)):
            number = reverse_ordering_keys[keys]
            prefx = '%s-%d-' % (prefix, new_idx)
            for field in values[number]:
                new_key = prefx + field
                new_values[new_key] = values[number][field]
        return new_values

    def _parcel_sorting(self, key):
        town, year, section, parcel = key
        # deal with parcel_number such as '34p' and convert to int
        parcel_number = ''
        for p in parcel:
            try:
                parcel_number += str(int(p))
            except ValueError:
                break
        if not parcel_number:
            parcel_number = 0
        else:
            parcel_number = int(parcel_number)
        return (town, year, section, parcel_number)

    def as_table(self):
        # add dynamic widget
        render = self.selection_form.as_table()
        render += super(FormSet, self).as_table()
        return mark_safe(render)

    def as_p(self):
        # add dynamic widget
        render = self.selection_form.as_p()
        render += super(FormSet, self).as_p()
        return mark_safe(render)

    def as_ul(self):
        # add dynamic widget
        render = self.selection_form.as_ul()
        render += super(FormSet, self).as_ul()
        return mark_safe(render)

    def add_fields(self, form, index):
        super(FormSet, self).add_fields(form, index)

    def clean(self):
        # manage parcel selection
        selected_town, parcels = None, []
        if self.data.get('_parcel_selection'):
            parcels = parse_parcels(self.data['_parcel_selection'])
            selected_town = self.data.get('_town')
            for idx, parcel in enumerate(parcels):
                parcel['town'] = selected_town
                parcel['DELETE'] = False
                parcels[idx] = parcel
            c_max = self.total_form_count()
            # pop the last extra form
            extra_form = self.forms.pop()
            for idx, parcel in enumerate(parcels):
                form = self._construct_form(idx + c_max)
                for k in parcel:
                    self.data[form.prefix + '-' + k] = parcel[k]
                # reconstruct with correct binded data
                form = self._construct_form(idx + c_max)
                form.cleaned_data = parcel
                self.forms.append(form)
                self._errors.append(None)
            self.forms.append(extra_form)
            self.data[self.prefix + '-' + TOTAL_FORM_COUNT] = c_max + \
                len(parcels)
            self.management_form.data = self.data
            self.management_form.is_valid()
        # Checks that no parcels are duplicated.
        self.check_duplicate(('town', 'section', 'parcel_number',
                             'year'), _(u"There are identical parcels."))
        if hasattr(self, 'cleaned_data') and self.cleaned_data:
            return self.cleaned_data

ParcelFormSet = formset_factory(ParcelForm, can_delete=True,
                                formset=ParcelFormSet)
ParcelFormSet.form_label = _(u"Parcels")


class RecordRelationsForm(forms.Form):
    base_model = 'right_relation'
    current_model = models.RelationType
    current_related_model = models.Operation
    associated_models = {'right_record': models.Operation,
                         'relation_type': models.RelationType}
    relation_type = forms.ChoiceField(label=_(u"Relation type"),
                                      choices=[], required=False)
    right_record = forms.IntegerField(
        label=_(u"Operation"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-operation'),
            associated_model=models.Operation),
        validators=[valid_id(models.Operation)], required=False)

    def __init__(self, *args, **kwargs):
        super(RecordRelationsForm, self).__init__(*args, **kwargs)
        self.fields['relation_type'].choices = \
            models.RelationType.get_types()

    @classmethod
    def _format_lst(cls, current):
        nc = []
        for rel, ope in sorted(current):
            if not nc or nc[-1][0] != rel:
                nc.append([rel, []])
            nc[-1][1].append(ope)
        rendered = u";".join(
            [u"{}{} {}".format(rel, _(u":"), u" ; ".join(opes))
             for rel, opes in nc])
        return rendered

    def clean(self):
        cleaned_data = self.cleaned_data
        if (cleaned_data.get('relation_type', None) and
                not cleaned_data.get('right_record', None)):
            raise forms.ValidationError(_(u"You should select an operation."))
        if (not cleaned_data.get('relation_type', None) and
                cleaned_data.get('right_record', None)):
            raise forms.ValidationError(
                _(u"You should select a relation type."))
        return cleaned_data

    @classmethod
    def get_formated_datas(cls, cleaned_datas):
        result, current, deleted = [], [], []
        for data in cleaned_datas:
            if not data:
                continue
            try:
                relation_type = cls.current_model.objects.get(
                    pk=data.get('relation_type'))
            except cls.current_model.DoesNotExist:
                continue
            try:
                right_record = cls.current_related_model.objects.get(
                    pk=data.get('right_record'))
            except cls.current_related_model.DoesNotExist:
                continue
            values = [unicode(relation_type), right_record.reference]
            if data.get('DELETE'):
                deleted.append(values)
            else:
                current.append(values)
        if current:
            nc = []
            for rel, ope in sorted(current):
                if not nc or nc[-1][0] != rel:
                    nc.append([rel, []])
                nc[-1][1].append(ope)
            result.append((_("Current relations"), cls._format_lst(current)))
        if deleted:
            result.append((_("Deleted relations"), u" ; ".join(deleted)))
        return result

RecordRelationsFormSet = formset_factory(RecordRelationsForm, can_delete=True)
RecordRelationsFormSet.form_label = _(u"Relations")

SRA_AGENT, created = PersonType.objects.get_or_create(txt_idx='sra_agent')
HEAD_SCIENTIST, created = PersonType.objects.get_or_create(
    txt_idx='head_scientist')

OPERATOR, created = OrganizationType.objects.get_or_create(txt_idx='operator')


class OperationSelect(TableSelect):
    year = forms.IntegerField(label=_("Year"))
    operation_code = forms.IntegerField(label=_(u"Numeric reference"))
    if settings.COUNTRY == 'fr':
        code_patriarche = forms.IntegerField(
            label="Numéro d'opération (OA Patriarche)")
    towns = get_town_field()
    parcel = ParcelField(label=_("Parcel (section/number)"))
    if settings.ISHTAR_DPTS:
        towns__numero_insee__startswith = forms.ChoiceField(
            label=_(u"Department"), choices=[])
    common_name = forms.CharField(label=_(u"Name"),
                                  max_length=30)
    operation_type = forms.ChoiceField(label=_(u"Operation type"),
                                       choices=[])
    end_date = forms.NullBooleanField(label=_(u"Is open?"))
    in_charge = forms.IntegerField(
        widget=widgets.JQueryAutoComplete(
            reverse_lazy(
                'autocomplete-person-permissive',
                args=["_".join(
                    [unicode(PersonType.objects.get(txt_idx='sra_agent').pk)])]
            ),
            associated_model=Person),
        label=_(u"In charge"))
    scientist = forms.IntegerField(
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person-permissive',
                         args=["_".join([unicode(HEAD_SCIENTIST.pk),
                                         unicode(SRA_AGENT.pk)])]),
            associated_model=Person),
        label=_(u"Scientist in charge"))
    operator = forms.IntegerField(
        label=_("Operator"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-organization', args=[OPERATOR.pk]),
            associated_model=Organization),
        validators=[valid_id(Organization)])
    # operator_reference = forms.CharField(label=_(u"Operator reference"),
    #                                      max_length=20)
    remains = forms.ChoiceField(label=_(u"Remains"), choices=[])
    periods = forms.ChoiceField(label=_(u"Periods"), choices=[])
    start_before = forms.DateField(label=_(u"Started before"),
                                   widget=widgets.JQueryDate)
    start_after = forms.DateField(label=_(u"Started after"),
                                  widget=widgets.JQueryDate)
    end_before = forms.DateField(label=_(u"Ended before"),
                                 widget=widgets.JQueryDate)
    end_after = forms.DateField(label=_(u"Ended after"),
                                widget=widgets.JQueryDate)
    relation_types = forms.MultipleChoiceField(
        label=_(u"Search within relations"), choices=[],
        widget=forms.CheckboxSelectMultiple)
    comment = forms.CharField(label=_(u"Comment"), max_length=500)
    abstract = forms.CharField(label=_(u"Abstract (full text search)"))
    record_quality = forms.ChoiceField(label=_(u"Record quality"))
    report_processing = forms.ChoiceField(label=_(u"Report processing"),
                                          choices=[])
    virtual_operation = forms.NullBooleanField(label=_(u"Virtual operation"))
    archaeological_sites = forms.IntegerField(
        label=_("Archaelogical site"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-archaeologicalsite'),
            associated_model=models.ArchaeologicalSite),
        validators=[valid_id(models.ArchaeologicalSite)])
    history_creator = forms.IntegerField(
        label=_(u"Created by"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person', args=['0', 'user']),
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
        super(OperationSelect, self).__init__(*args, **kwargs)
        self.fields['operation_type'].choices = \
            models.OperationType.get_types()
        self.fields['operation_type'].help_text = \
            models.OperationType.get_help()
        self.fields['report_processing'].choices = \
            models.ReportState.get_types()
        self.fields['report_processing'].help_text = \
            models.ReportState.get_help()
        self.fields['remains'].choices = models.RemainType.get_types()
        self.fields['remains'].help_text = models.RemainType.get_help()
        self.fields['periods'].choices = models.Period.get_types()
        self.fields['periods'].help_text = models.Period.get_help()
        self.fields['record_quality'].choices = \
            [('', '--')] + list(models.QUALITY)
        if settings.ISHTAR_DPTS:
            k = 'towns__numero_insee__startswith'
            self.fields[k].choices = [
                ('', '--')] + list(settings.ISHTAR_DPTS)
        self.fields['relation_types'].choices = models.RelationType.get_types(
            empty_first=False)

    def get_input_ids(self):
        ids = super(OperationSelect, self).get_input_ids()
        ids.pop(ids.index('parcel'))
        ids.append('parcel_0')
        ids.append('parcel_1')
        ids.pop(ids.index('relation_types'))
        for idx, c in enumerate(self.fields['relation_types'].choices):
            ids.append('relation_types_{}'.format(idx))
        return ids


class OperationFormSelection(forms.Form):
    form_label = _(u"Operation search")
    associated_models = {'pk': models.Operation}
    currents = {'pk': models.Operation}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-operation'), OperationSelect, models.Operation,
            source_full=reverse_lazy('get-operation-full')),
        validators=[valid_id(models.Operation)])

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'pk' not in cleaned_data or not cleaned_data['pk']:
            raise forms.ValidationError(_(u"You should select an operation."))
        return cleaned_data


class OperationCodeInput(forms.TextInput):
    """Manage auto complete when changing year in form"""
    def render(self, *args, **kwargs):
        name, value = args
        base_name = '-'.join(name.split('-')[:-1])
        rendered = super(OperationCodeInput, self).render(*args, **kwargs)
        js = u"""\n    <script type="text/javascript"><!--//
        function initialyse_operation_code () {
            // if the form is in creation mode
            if(!$("#id_%(base_name)s-pk").val()){
                $("#id_%(base_name)s-year").change(function() {
                    var year = $("#id_%(base_name)s-year").val();
                    var url = "%(url)s" + year;
                    $.getJSON(url, function(data) {
                        $("#id_%(name)s").val(data.id);
                    });
                });
            }
        }
        $(document).ready(initialyse_operation_code());
        //--></script>\n""" % {
            'base_name': base_name, 'name': name,
            'url': reverse_lazy('get_available_operation_code')}
        return mark_safe(rendered + js)


class OperationFormFileChoice(forms.Form):
    form_label = _(u"Associated file")
    associated_models = {'associated_file': File, }
    currents = {'associated_file': File}
    associated_file = forms.IntegerField(
        label=_(u"Archaelogical file"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-file'), associated_model=File),
        validators=[valid_id(File)], required=False)


class OperationFormAbstract(forms.Form):
    form_label = _(u"Abstract")
    abstract = forms.CharField(
        label=_(u"Abstract"),
        widget=forms.Textarea(attrs={'class': 'xlarge'}), required=False)

SLICING = (("month", _(u"months")), ('year', _(u"years")),)

DATE_SOURCE = (('creation', _(u"Creation date")),
               ("start", _(u"Start of field work")))

PREVENTIVE_RESARCH = (('all', _('All')),
                      ('preventive', _(u"Preventive")),
                      ('research', _(u"Research")),)


class DashboardForm(forms.Form):
    slicing = forms.ChoiceField(label=_("Slicing"), choices=SLICING,
                                required=False)
    department_detail = forms.BooleanField(
        label=_("Department detail"), required=False)
    date_source = forms.ChoiceField(
        label=_("Date get from"), choices=DATE_SOURCE, required=False)
    preventive_research = forms.ChoiceField(
        label=_("Preventive/Research"), choices=PREVENTIVE_RESARCH,
        required=False)
    operation_type = forms.ChoiceField(label=_("Operation type"), choices=[],
                                       required=False)
    operator = forms.ChoiceField(label=_("Operator"), choices=[],
                                 required=False)
    after = forms.DateField(label=_(u"Date after"),
                            widget=widgets.JQueryDate, required=False)
    before = forms.DateField(label=_(u"Date before"),
                             widget=widgets.JQueryDate, required=False)
    with_report = forms.BooleanField(label=_("With reports"), required=False)
    with_finds = forms.BooleanField(label=_("With finds"), required=False)

    def __init__(self, *args, **kwargs):
        if 'prefix' not in kwargs:
            kwargs['prefix'] = 'operations'
        super(DashboardForm, self).__init__(*args, **kwargs)
        self.fields['operation_type'].choices = \
            models.OperationType.get_types()
        self.fields['operator'].choices = [('', '--')]
        self.fields['operator'].choices += [
            (orga.pk, orga.name)
            for orga in Organization.objects.filter(operator__isnull=False)
                                            .order_by('name').distinct().all()]

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
        if self.cleaned_data.get('preventive_research'):
            preventive_research = self.cleaned_data['preventive_research']
            if preventive_research == 'preventive':
                fltr['file_type__preventive'] = True
            elif preventive_research == 'preventive':
                fltr['file_type__preventive'] = False
        if self.cleaned_data.get('operation_type'):
            fltr['operation_type_id'] = self.cleaned_data['operation_type']
        if self.cleaned_data.get('operator'):
            fltr['operator_id'] = self.cleaned_data['operator']
        if self.cleaned_data.get('after'):
            fltr[date_source + '_date__gte'] = self.cleaned_data['after']
        if self.cleaned_data.get('before'):
            fltr[date_source + '_date__lte'] = self.cleaned_data['before']
        if self.cleaned_data.get('with_report'):
            fltr['report_delivery_date__isnull'] = False
        if self.cleaned_data.get('with_finds'):
            fltr['context_record__base_finds__isnull'] = False
        return fltr


class OperationFormGeneral(forms.Form):
    form_label = _(u"General")
    base_model = 'archaeological_site'
    associated_models = {'scientist': Person,
                         'in_charge': Person,
                         'cira_rapporteur': Person,
                         'operator': Organization,
                         'operation_type': models.OperationType,
                         'report_processing': models.ReportState,
                         }
    pk = forms.IntegerField(required=False, widget=forms.HiddenInput)
    if settings.COUNTRY == 'fr':
        code_patriarche = forms.IntegerField(label=u"Code PATRIARCHE",
                                             required=False)
    common_name = forms.CharField(label=_(u"Generic name"), required=False,
                                  max_length=120, widget=forms.Textarea)
    operation_type = forms.ChoiceField(label=_(u"Operation type"),
                                       choices=[])
    year = forms.IntegerField(label=_(u"Year"),
                              initial=lambda: datetime.datetime.now().year,
                              validators=[validators.MinValueValidator(1900),
                                          validators.MaxValueValidator(2100)])
    scientist = forms.IntegerField(
        label=_("Head scientist"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=["_".join([unicode(HEAD_SCIENTIST.pk),
                                         unicode(SRA_AGENT.pk)])]),
            associated_model=Person,
            limit={'person_types': (HEAD_SCIENTIST.pk, SRA_AGENT.pk)},
            new=True),
        validators=[valid_id(Person)], required=False)
    operator = forms.IntegerField(
        label=_("Operator"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-organization', args=[OPERATOR.pk]),
            limit={'organization_type': (OPERATOR.pk,)},
            associated_model=Organization, new=True),
        validators=[valid_id(Organization)], required=False)
    operator_reference = forms.CharField(label=_(u"Operator reference"),
                                         required=False, max_length=20)
    in_charge = forms.IntegerField(
        label=_("In charge"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person',
                         args=["_".join([unicode(SRA_AGENT.pk)])]),
            associated_model=Person,
            limit={'person_types': [SRA_AGENT.pk]}, new=True),
        validators=[valid_id(Person)], required=False)
    surface = forms.IntegerField(
        required=False, widget=widgets.AreaWidget,
        label=_(u"Total surface (m2)"),
        validators=[validators.MinValueValidator(0),
                    validators.MaxValueValidator(999999999)])
    # archaeological_site = widgets.MultipleAutocompleteField(
    #     model=models.ArchaeologicalSite,
    #     label=_("Associated archaeological sites"), new=True, required=False)
    start_date = forms.DateField(
        label=_(u"Start date"), required=False, widget=widgets.JQueryDate)
    excavation_end_date = forms.DateField(
        label=_(u"Excavation end date"), required=False,
        widget=widgets.JQueryDate)
    report_delivery_date = forms.DateField(
        label=_(u"Report delivery date"), required=False,
        widget=widgets.JQueryDate)
    report_processing = forms.ChoiceField(label=_(u"Report processing"),
                                          choices=[], required=False)
    if settings.COUNTRY == 'fr':
        code_dracar = forms.CharField(
            label=u"Code DRACAR", required=False,
            validators=[validators.MaxLengthValidator(10)])
        cira_date = forms.DateField(label=u"Date avis CIRA", required=False,
                                    widget=widgets.JQueryDate)
        negative_result = forms.NullBooleanField(
            required=False, label=u"Résultat considéré comme négatif")
        cira_rapporteur = forms.IntegerField(
            label=u"Rapporteur CIRA",
            widget=widgets.JQueryAutoComplete(
                reverse_lazy('autocomplete-person',
                             args=["_".join([unicode(HEAD_SCIENTIST.pk),
                                             unicode(SRA_AGENT.pk)])]),
                limit={'person_types': [SRA_AGENT.pk, HEAD_SCIENTIST.pk]},
                associated_model=Person, new=True),
            validators=[valid_id(Person)], required=False)
    comment = forms.CharField(label=_(u"Comment"), widget=forms.Textarea,
                              required=False)
    record_quality = forms.ChoiceField(label=_(u"Record quality"),
                                       required=False)
    virtual_operation = forms.BooleanField(required=False,
                                           label=_(u"Virtual operation"))

    def __init__(self, *args, **kwargs):
        super(OperationFormGeneral, self).__init__(*args, **kwargs)
        self.fields['operation_type'].choices = \
            models.OperationType.get_types()
        self.fields['operation_type'].help_text = \
            models.OperationType.get_help()
        self.fields['report_processing'].choices = \
            models.ReportState.get_types()
        self.fields['report_processing'].help_text = \
            models.ReportState.get_help()
        self.fields['record_quality'].choices = \
            [('', '--')] + list(models.QUALITY)
        if 'operation_code' in self.fields:
            self.fields.keyOrder = list(self.fields.keyOrder)
            self.fields.keyOrder.pop(self.fields.keyOrder.index(
                'operation_code'))
            self.fields.keyOrder.insert(self.fields.keyOrder.index('year'),
                                        'operation_code')

    def clean(self):
        cleaned_data = self.cleaned_data
        # verify the logic between start date and excavation end date
        if cleaned_data.get('excavation_end_date'):
            if not self.cleaned_data['start_date']:
                raise forms.ValidationError(
                    _(u"If you want to set an excavation end date you have to "
                      u"provide a start date."))
            if cleaned_data['excavation_end_date'] \
                    < cleaned_data['start_date']:
                raise forms.ValidationError(
                    _(u"The excavation end date cannot be before the start "
                      u"date."))
        year = self.cleaned_data.get("year")
        operation_code = cleaned_data.get("operation_code", None)
        if not operation_code:
            return self.cleaned_data
        ops = models.Operation.objects.filter(year=year,
                                              operation_code=operation_code)
        # manage unique operation ID
        if 'pk' in cleaned_data and cleaned_data['pk']:
            ops = ops.exclude(pk=cleaned_data['pk'])
        if ops.count():
            max_val = models.Operation.objects.filter(year=year).aggregate(
                Max('operation_code'))["operation_code__max"]
            msg = ''
            if year and max_val:
                msg = _(
                    u"Operation code already exist for year: %(year)d - use a "
                    u"value bigger than %(last_val)d") % {
                    'year': year, 'last_val': max_val}
            else:
                msg = _(u"Bad operation code")
            raise forms.ValidationError(msg)
        return self.cleaned_data


class OperationFormModifGeneral(OperationFormGeneral):
    operation_code = forms.IntegerField(label=_(u"Operation code"),
                                        required=False)
    currents = {'associated_file': File}
    associated_file = forms.IntegerField(
        label=_(u"Archaelogical file"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-file'),
            associated_model=File),
        validators=[valid_id(File)], required=False)

    def __init__(self, *args, **kwargs):
        super(OperationFormModifGeneral, self).__init__(*args, **kwargs)
        self.fields.keyOrder = list(self.fields.keyOrder)
        self.fields.keyOrder.pop(self.fields.keyOrder.index('associated_file'))
        self.fields.keyOrder.insert(self.fields.keyOrder.index('in_charge'),
                                    'associated_file')
        if not get_current_profile().files:
            self.fields.pop('associated_file')

OperationFormModifGeneral.associated_models = \
    OperationFormGeneral.associated_models.copy()

OperationFormModifGeneral.associated_models['associated_file'] = File


class OperationFormPreventive(forms.Form):
    form_label = _(u"Preventive informations - excavation")
    cost = forms.IntegerField(label=_(u"Cost (euros)"), required=False)
    scheduled_man_days = forms.IntegerField(label=_(u"Scheduled man-days"),
                                            required=False)
    optional_man_days = forms.IntegerField(label=_(u"Optional man-days"),
                                           required=False)
    effective_man_days = forms.IntegerField(label=_(u"Effective man-days"),
                                            required=False)
    if settings.COUNTRY == 'fr':
        fnap_financing = forms.FloatField(
            required=False, label=u"Pourcentage de financement FNAP",
            validators=[validators.MinValueValidator(0),
                        validators.MaxValueValidator(100)])


class OperationFormPreventiveDiag(forms.Form):
    form_label = _("Preventive informations - diagnostic")
    if settings.COUNTRY == 'fr':
        zoning_prescription = forms.NullBooleanField(
            required=False, label=_(u"Prescription on zoning"))
        large_area_prescription = forms.NullBooleanField(
            required=False, label=_(u"Prescription on large area"))
        geoarchaeological_context_prescription = forms.NullBooleanField(
            required=False,
            label=_(u"Prescription on geoarchaeological context"))


class SelectedTownForm(forms.Form):
    form_label = _("Towns")
    associated_models = {'town': Town}
    town = forms.ChoiceField(label=_("Town"), choices=(),
                             validators=[valid_id(Town)])

    def __init__(self, *args, **kwargs):
        towns = None
        if 'data' in kwargs and 'TOWNS' in kwargs['data']:
            towns = kwargs['data']['TOWNS']
            # clean data if not "real" data
            prefix_value = kwargs['prefix'] + '-town'
            if not [k for k in kwargs['data'].keys()
                    if k.startswith(prefix_value) and kwargs['data'][k]]:
                kwargs['data'] = None
                if 'files' in kwargs:
                    kwargs.pop('files')
        super(SelectedTownForm, self).__init__(*args, **kwargs)
        if towns and towns != -1:
            self.fields['town'].choices = [('', '--')] + towns

SelectedTownFormset = formset_factory(SelectedTownForm, can_delete=True,
                                      formset=TownFormSet)
SelectedTownFormset.form_label = _(u"Towns")


class SelectedParcelForm(forms.Form):
    form_label = _("Parcels")
    associated_models = {'parcel': models.Parcel}
    parcel = forms.ChoiceField(
        label=_("Parcel"), choices=(), validators=[valid_id(models.Parcel)])

    def __init__(self, *args, **kwargs):
        parcels = None
        if 'data' in kwargs and 'PARCELS' in kwargs['data']:
            parcels = kwargs['data']['PARCELS']
            # clean data if not "real" data
            prefix_value = kwargs['prefix'] + '-parcel'
            if not [k for k in kwargs['data'].keys()
                    if k.startswith(prefix_value) and kwargs['data'][k]]:
                kwargs['data'] = None
                if 'files' in kwargs:
                    kwargs.pop('files')
        super(SelectedParcelForm, self).__init__(*args, **kwargs)
        if parcels:
            self.fields['parcel'].choices = [('', '--')] + parcels

SelectedParcelFormSet = formset_factory(SelectedParcelForm, can_delete=True,
                                        formset=ParcelFormSet)
SelectedParcelFormSet.form_label = _("Parcels")

SelectedParcelGeneralFormSet = formset_factory(ParcelForm, can_delete=True,
                                               formset=ParcelFormSet)
SelectedParcelGeneralFormSet.form_label = _("Parcels")

"""
class SelectedParcelFormSet(forms.Form):
    form_label = _("Parcels")
    base_model = 'parcel'
    associated_models = {'parcel': models.Parcel}
    parcel = forms.MultipleChoiceField(
        label=_("Parcel"), required=False, choices=[],
        widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        parcels = None
        if 'data' in kwargs and 'PARCELS' in kwargs['data']:
            parcels = kwargs['data']['PARCELS']
            # clean data if not "real" data
            prefix_value = kwargs['prefix'] + '-parcel'
            if not [k for k in kwargs['data'].keys()
                    if k.startswith(prefix_value) and kwargs['data'][k]]:
                kwargs['data'] = None
                if 'files' in kwargs:
                    kwargs.pop('files')
        super(SelectedParcelFormSet, self).__init__(*args, **kwargs)
        if parcels:
            self.fields['parcel'].choices = [('', '--')] + parcels
"""


class RemainForm(forms.Form):
    form_label = _("Remain types")
    base_model = 'remain'
    associated_models = {'remain': models.RemainType}
    remain = forms.MultipleChoiceField(
        label=_("Remain type"), required=False, choices=[],
        widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(RemainForm, self).__init__(*args, **kwargs)
        self.fields['remain'].choices = models.RemainType.get_types(
            empty_first=False)
        self.fields['remain'].help_text = models.RemainType.get_help()


class PeriodForm(forms.Form):
    form_label = _("Periods")
    base_model = 'period'
    associated_models = {'period': models.Period}
    period = forms.MultipleChoiceField(
        label=_("Period"), required=False, choices=[],
        widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super(PeriodForm, self).__init__(*args, **kwargs)
        self.fields['period'].choices = models.Period.get_types(
            empty_first=False)
        self.fields['period'].help_text = models.Period.get_help()


class ArchaeologicalSiteForm(forms.Form):
    reference = forms.CharField(label=_(u"Reference"), max_length=20)
    name = forms.CharField(label=_(u"Name"), max_length=200, required=False)
    periods = forms.MultipleChoiceField(
        label=_("Periods"), choices=[], widget=widgets.Select2Multiple,
        required=False)
    remains = forms.MultipleChoiceField(
        label=_("Remains"), choices=[], widget=widgets.Select2Multiple,
        required=False)

    def __init__(self, *args, **kwargs):
        self.limits = {}
        if 'limits' in kwargs:
            kwargs.pop('limits')
        super(ArchaeologicalSiteForm, self).__init__(*args, **kwargs)
        self.fields['periods'].choices = \
            models.Period.get_types(empty_first=False)
        self.fields['periods'].help_text = models.Period.get_help()
        self.fields['remains'].choices = \
            models.RemainType.get_types(empty_first=False)
        self.fields['remains'].help_text = models.RemainType.get_help()

    def clean_reference(self):
        reference = self.cleaned_data['reference']
        if models.ArchaeologicalSite.objects\
                                    .filter(reference=reference).count():
            raise forms.ValidationError(_(u"This reference already exists."))
        return reference

    def save(self, user):
        dct = self.cleaned_data
        dct['history_modifier'] = user
        periods = dct.pop('periods')
        remains = dct.pop('remains')
        item = models.ArchaeologicalSite.objects.create(**dct)
        for period in periods:
            item.periods.add(period)
        for remain in remains:
            item.remains.add(remain)
        return item


class ArchaeologicalSiteBasicForm(forms.Form):
    form_label = _("Archaeological site")
    base_model = 'archaeological_site'
    associated_models = {'archaeological_site': models.ArchaeologicalSite}
    archaeological_site = forms.IntegerField(
        label=_("Archaelogical site"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-archaeologicalsite'),
            associated_model=models.ArchaeologicalSite,
            new=True),
        validators=[valid_id(models.ArchaeologicalSite)],
        required=False)


ArchaeologicalSiteFormSet = formset_factory(ArchaeologicalSiteBasicForm,
                                            can_delete=True, formset=FormSet)
ArchaeologicalSiteFormSet.form_label = _("Archaeological sites")


class ArchaeologicalSiteSelectionForm(forms.Form):
    form_label = _("Associated archaelogical sites")
    archaeological_sites = forms.IntegerField(
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-archaeologicalsite'),
            associated_model=models.ArchaeologicalSite, new=True,
            multiple=True),
        label=_(u"Search"))


class FinalOperationClosingForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to close this operation?")


class OperationDeletionForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to delete this operation?")

####################################
# Source management for operations #
####################################


class OperationSourceForm(SourceForm):
    pk = forms.IntegerField(required=False, widget=forms.HiddenInput)
    index = forms.IntegerField(label=_(u"Index"))
    hidden_operation_id = forms.IntegerField(label="",
                                             widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super(OperationSourceForm, self).__init__(*args, **kwargs)
        keyOrder = self.fields.keyOrder
        keyOrder.pop(keyOrder.index('index'))
        keyOrder.insert(keyOrder.index('source_type') + 1, 'index')

    def clean(self):
        # manage unique operation ID
        cleaned_data = self.cleaned_data
        operation_id = cleaned_data.get("hidden_operation_id")
        index = cleaned_data.get("index")
        srcs = models.OperationSource.objects\
                                     .filter(index=index,
                                             operation__pk=operation_id)
        if 'pk' in cleaned_data and cleaned_data['pk']:
            srcs = srcs.exclude(pk=cleaned_data['pk'])
        if srcs.count():
            max_val = models.OperationSource.objects\
                            .filter(operation__pk=operation_id)\
                            .aggregate(Max('index'))["index__max"]
            operation = models.Operation.objects.get(pk=operation_id)
            raise forms.ValidationError(
                _(u"Index already exists for operation: %(operation)s - use a "
                  u"value bigger than %(last_val)d") % {
                    "operation": unicode(operation), 'last_val': max_val})
        return cleaned_data

SourceOperationFormSelection = get_form_selection(
    'SourceOperationFormSelection', _(u"Operation search"), 'operation',
    models.Operation, OperationSelect, 'get-operation',
    _(u"You should select an operation."))


class OperationSourceSelect(SourceSelect):
    operation__towns = get_town_field(label=_(u"Operation's town"))
    operation__operation_type = forms.ChoiceField(label=_(u"Operation type"),
                                                  choices=[])
    operation__year = forms.IntegerField(label=_(u"Operation's year"))

    def __init__(self, *args, **kwargs):
        super(OperationSourceSelect, self).__init__(*args, **kwargs)
        self.fields['operation__operation_type'].choices = \
            models.OperationType.get_types()
        self.fields['operation__operation_type'].help_text = \
            models.OperationType.get_help()


OperationSourceFormSelection = get_form_selection(
    'OperationSourceFormSelection', _(u"Documentation search"), 'pk',
    models.OperationSource, OperationSourceSelect, 'get-operationsource',
    _(u"You should select a document."),
    get_full_url='get-operationsource-full')

################################################
# Administrative act management for operations #
################################################


class AdministrativeActOpeSelect(TableSelect):
    year = forms.IntegerField(label=_("Year"))
    index = forms.IntegerField(label=_("Index"))
    if settings.COUNTRY == 'fr':
        ref_sra = forms.CharField(label=u"Autre référence",
                                  max_length=15)
        operation__code_patriarche = forms.IntegerField(
            label="Numéro d'opération (OA Patriarche)")
    act_type = forms.ChoiceField(label=_("Act type"), choices=[])
    indexed = forms.NullBooleanField(label=_(u"Indexed?"))
    operation__towns = get_town_field()
    parcel = ParcelField(label=_("Parcel (section/number)"))
    if settings.ISHTAR_DPTS:
        operation__towns__numero_insee__startswith = forms.ChoiceField(
            label=_(u"Department"), choices=[])
    act_object = forms.CharField(label=_(u"Object"),
                                 max_length=300)
    history_creator = forms.IntegerField(
        label=_(u"Created by"),
        widget=widgets.JQueryAutoComplete(
            reverse_lazy('autocomplete-person', args=['0', 'user']),
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
        super(AdministrativeActOpeSelect, self).__init__(*args, **kwargs)
        self.fields['act_type'].choices = models.ActType.get_types(
            dct={'intented_to': 'O'})
        self.fields['act_type'].help_text = models.ActType.get_help(
            dct={'intented_to': 'O'})
        if settings.ISHTAR_DPTS:
            k = 'operation__towns__numero_insee__startswith'
            self.fields[k].choices = [
                ('', '--')] + list(settings.ISHTAR_DPTS)

    def get_input_ids(self):
        ids = super(AdministrativeActOpeSelect, self).get_input_ids()
        ids.pop(ids.index('parcel'))
        ids.append('parcel_0')
        ids.append('parcel_1')
        return ids


class AdministrativeActOpeFormSelection(forms.Form):
    form_label = _("Administrative act search")
    associated_models = {'pk': models.AdministrativeAct}
    currents = {'pk': models.AdministrativeAct}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-administrativeactop'),
            AdministrativeActOpeSelect, models.AdministrativeAct,
            table_cols='TABLE_COLS_OPE'),
        validators=[valid_id(models.AdministrativeAct)])

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'pk' not in cleaned_data or not cleaned_data['pk']:
            raise forms.ValidationError(
                _(u"You should select an administrative act."))
        return cleaned_data


class AdministrativeActOpeForm(forms.Form):
    form_label = _("General")
    associated_models = {'act_type': models.ActType, }
    #                     'signatory':Person}
    act_type = forms.ChoiceField(label=_("Act type"), choices=[])
    # signatory = forms.IntegerField(label=_("Signatory"),
    #     widget=widgets.JQueryAutoComplete(reverse_lazy('autocomplete-person'),
    #                                 associated_model=Person, new=True),
    #     validators=[valid_id(Person)], required=False)
    act_object = forms.CharField(label=_(u"Object"), max_length=300,
                                 widget=forms.Textarea, required=False)
    signature_date = forms.DateField(
        label=_(u"Signature date"), initial=get_now, widget=widgets.JQueryDate)
    if settings.COUNTRY == 'fr':
        ref_sra = forms.CharField(label=u"Autre référence", max_length=15,
                                  required=False)

    def __init__(self, *args, **kwargs):
        super(AdministrativeActOpeForm, self).__init__(*args, **kwargs)
        self.fields['act_type'].choices = models.ActType.get_types(
            dct={'intented_to': 'O'})
        self.fields['act_type'].help_text = models.ActType.get_help(
            dct={'intented_to': 'O'})


class FinalAdministrativeActDeleteForm(FinalForm):
    confirm_msg = " "
    confirm_end_msg = _(u"Would you like to delete this administrative act?")


class DocumentGenerationAdminActForm(forms.Form):
    _associated_model = models.AdministrativeAct
    document_template = forms.ChoiceField(label=_("Template"), choices=[])

    def __init__(self, *args, **kwargs):
        self.document_type = 'O'
        if 'operation' in kwargs:
            self.document_type = 'O' if kwargs.pop('operation') else 'F'
        self.obj = None
        if 'obj' in kwargs:
            self.obj = kwargs.pop('obj')
        super(DocumentGenerationAdminActForm, self).__init__(*args, **kwargs)
        self.fields['document_template'].choices = DocumentTemplate.get_tuples(
            dct={'associated_object_name':
                 'archaeological_operations.models.AdministrativeAct',
                 'acttypes__intented_to': self.document_type})

    def clean(self):
        if not self.obj:
            raise forms.ValidationError(
                _(u"You should select an administrative act."))
        cleaned_data = self.cleaned_data
        try:
            dt = DocumentTemplate.objects.get(
                pk=self.cleaned_data['document_template'])
        except DocumentTemplate.DoesNotExist:
            raise forms.ValidationError(_(u"This document is not intended for "
                                          u"this type of act."))
        if self.obj.act_type.pk not in [
                act_type.pk for act_type in dt.acttypes.all()]:
            raise forms.ValidationError(_(u"This document is not intended for "
                                          u"this type of act."))
        return cleaned_data

    def save(self, object_pk):
        try:
            c_object = self._associated_model.objects.get(pk=object_pk)
        except self._associated_model.DoesNotExist:
            return
        try:
            template = DocumentTemplate.objects.get(
                pk=self.cleaned_data.get('document_template'))
        except DocumentTemplate.DoesNotExist:
            return
        return template.publish(c_object)


class GenerateDocForm(forms.Form):
    form_label = _("Doc generation")
    doc_generation = forms.ChoiceField(
        required=False, choices=[], label=_(u"Generate the associated doc?"))

    def __init__(self, *args, **kwargs):
        choices = []
        if 'choices' in kwargs:
            choices = kwargs.pop('choices')
        super(GenerateDocForm, self).__init__(*args, **kwargs)
        self.fields['doc_generation'].choices = [('', u'-' * 9)] + \
            [(choice.pk, unicode(choice)) for choice in choices]


class AdministrativeActRegisterSelect(AdministrativeActOpeSelect):
    indexed = forms.NullBooleanField(label=_(u"Indexed?"))

    def __init__(self, *args, **kwargs):
        super(AdministrativeActRegisterSelect, self).__init__(*args, **kwargs)
        self.fields['act_type'].choices = models.ActType.get_types()
        self.fields['act_type'].help_text = models.ActType.get_help()


class AdministrativeActRegisterFormSelection(forms.Form):
    form_label = pgettext_lazy('admin act register', u"Register")
    associated_models = {'pk': models.AdministrativeAct}
    currents = {'pk': models.AdministrativeAct}
    pk = forms.IntegerField(
        label="", required=False,
        widget=widgets.JQueryJqGrid(
            reverse_lazy('get-administrativeact'),
            AdministrativeActRegisterSelect, models.AdministrativeAct,
            table_cols='TABLE_COLS',
            source_full=reverse_lazy('get-administrativeact-full')),
        validators=[valid_id(models.AdministrativeAct)])

    def clean(self):
        cleaned_data = self.cleaned_data
        if 'pk' not in cleaned_data or not cleaned_data['pk']:
            raise forms.ValidationError(
                _(u"You should select an administrative act."))
        return cleaned_data
