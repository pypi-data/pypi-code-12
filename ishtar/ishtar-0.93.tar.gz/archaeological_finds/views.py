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

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from ishtar_common.forms import FinalForm
from ishtar_common.forms_common import SourceForm, AuthorFormset, \
    SourceDeletionForm
from archaeological_context_records.forms import RecordFormSelection

from ishtar_common.views import get_item, show_item, revert_item, \
    get_autocomplete_generic
from ishtar_common.wizards import SearchWizard

from wizards import *
from forms import *
import models

find_extra_keys = {
    'base_finds__cache_short_id':
        'base_finds__cache_short_id__icontains',
    'base_finds__cache_complete_id':
        'base_finds__cache_complete_id__icontains',
    'label':
        'label__icontains',
    'base_finds__context_record':
        'base_finds__context_record__pk',
    'base_finds__context_record__parcel__town':
        'base_finds__context_record__parcel__town',
    'base_finds__context_record__operation__year':
        'base_finds__context_record__operation__year__contains',
    'base_finds__context_record__operation':
        'base_finds__context_record__operation__pk',
    'archaeological_sites':
        'base_finds__context_record__operation__archaeological_sites__pk',
    'base_finds__context_record__operation__code_patriarche':
        'base_finds__context_record__operation__code_patriarche',
    'datings__period': 'datings__period__pk',
    'base_finds__find__description':
        'base_finds__find__description__icontains',
    'base_finds__batch': 'base_finds__batch',
    'image': 'image__isnull'}

get_find = get_item(
    models.Find, 'get_find', 'find',
    reversed_bool_fields=['image__isnull'],
    base_request={'downstream_treatment__isnull': True},
    extra_request_keys=find_extra_keys.copy())

get_find_for_ope = get_item(
    models.Find, 'get_find', 'find',
    reversed_bool_fields=['image__isnull'],
    base_request={'downstream_treatment__isnull': True},
    extra_request_keys=find_extra_keys.copy(),
    own_table_cols=models.Find.TABLE_COLS_FOR_OPE)

show_findsource = show_item(models.FindSource, 'findsource')

get_findsource = get_item(
    models.FindSource, 'get_findsource', 'findsource',
    bool_fields=['duplicate'],
    extra_request_keys={
        'title': 'title__icontains',
        'description': 'description__icontains',
        'comment': 'comment__icontains',
        'additional_information': 'additional_information__icontains',
        'find__context_record__operation__year':
            'find__context_record__operation__year',
        'find__datings__period': 'find__datings__period__pk',
        'find__description': 'find__description__icontains',
    })
show_find = show_item(models.Find, 'find')
revert_find = revert_item(models.Find)

find_creation_wizard = FindWizard.as_view([
    ('selecrecord-find_creation', RecordFormSelection),
    ('find-find_creation', FindForm),
    ('dating-find_creation', DatingFormSet),
    ('final-find_creation', FinalForm)],
    label=_(u"New find"),
    url_name='find_creation',)

find_search_wizard = SearchWizard.as_view([
    ('general-find_search', FindFormSelection)],
    label=_(u"Find search"),
    url_name='find_search',)

find_modification_wizard = FindModificationWizard.as_view([
    ('selec-find_modification', FindFormSelection),
    ('find-find_modification', FindForm),
    ('dating-find_modification', DatingFormSet),
    ('final-find_modification', FinalForm)],
    label=_(u"Find modification"),
    url_name='find_modification',)


def find_modify(request, pk):
    # view = find_modification_wizard(request)
    FindModificationWizard.session_set_value(
        request, 'selec-find_modification', 'pk', pk, reset=True)
    return redirect(
        reverse('find_modification',
                kwargs={'step': 'find-find_modification'}))

find_deletion_wizard = FindDeletionWizard.as_view([
    ('selec-find_deletion', FindFormSelection),
    ('final-find_deletion', FindDeletionForm)],
    label=_(u"Find deletion"),
    url_name='find_deletion',)


find_source_creation_wizard = FindSourceWizard.as_view([
    ('selec-find_source_creation', SourceFindFormSelection),
    ('source-find_source_creation', SourceForm),
    ('authors-find_source_creation', AuthorFormset),
    ('final-find_source_creation', FinalForm)],
    label=_(u"Find: new source"),
    url_name='find_source_creation',)

find_source_modification_wizard = FindSourceWizard.as_view([
    ('selec-find_source_modification', FindSourceFormSelection),
    ('source-find_source_modification', SourceForm),
    ('authors-find_source_modification', AuthorFormset),
    ('final-find_source_modification', FinalForm)],
    label=_(u"Find: source modification"),
    url_name='find_source_modification',)

find_source_deletion_wizard = FindSourceDeletionWizard.as_view([
    ('selec-find_source_deletion', FindSourceFormSelection),
    ('final-find_source_deletion', SourceDeletionForm)],
    label=_(u"Find: source deletion"),
    url_name='find_source_deletion',)

autocomplete_objecttype = get_autocomplete_generic(models.ObjectType)
autocomplete_materialtype = get_autocomplete_generic(models.MaterialType)
autocomplete_preservationtype = get_autocomplete_generic(
    models.PreservationType)
autocomplete_integritytype = get_autocomplete_generic(models.IntegrityType)

"""
treatment_creation_wizard = TreatmentWizard.as_view([
    ('basetreatment-treatment_creation', BaseTreatmentForm),
    ('selecfind-treatment_creation', UpstreamFindFormSelection),
    ('multiselecfinds-treatment_creation', FindMultipleFormSelection),
    ('container-treatment_creation', ContainerForm),
    ('resultfind-treatment_creation', ResultFindForm),
    ('resultfinds-treatment_creation', ResultFindFormSet),
    ('final-treatment_creation', FinalForm)],
    condition_dict={
        'selecfind-treatment_creation':
            check_treatment('basetreatment-treatment_creation',
                          'treatment_type', not_type_list=['physical_grouping',
                                                           'packaging']),
        'multiselecfinds-treatment_creation':
            check_treatment('basetreatment-treatment_creation',
                            'treatment_type', ['physical_grouping',
                                               'packaging']),
        'resultfinds-treatment_creation':
            check_treatment('basetreatment-treatment_creation',
                            'treatment_type', ['split']),
        'resultfind-treatment_creation':
            check_treatment('basetreatment-treatment_creation',
                            'treatment_type', not_type_list=['split']),
        'container-treatment_creation':
            check_treatment('basetreatment-treatment_creation',
                            'treatment_type', ['packaging']),
    },
    label=_(u"New treatment"),
    url_name='treatment_creation',)
"""

"""
treatment_source_creation_wizard = TreatmentSourceWizard.as_view([
    ('selec-treatment_source_creation', SourceTreatmentFormSelection),
    ('source-treatment_source_creation', SourceForm),
    ('authors-treatment_source_creation', AuthorFormset),
    ('final-treatment_source_creation', FinalForm)],
    url_name='treatment_source_creation',)

"""
