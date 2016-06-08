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

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, FormView

from ishtar_common.forms import FinalForm
from ishtar_common.forms_common import SourceForm, AuthorFormset, \
    SourceDeletionForm
from ishtar_common.models import IshtarUser
from archaeological_context_records.forms \
    import RecordFormSelection as RecordFormSelectionTable

from ishtar_common.views import get_item, show_item, revert_item, \
    get_autocomplete_generic, IshtarMixin, LoginRequiredMixin
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
    'basket': 'basket',
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

show_findbasket = show_item(models.FindBasket, 'findbasket')

find_creation_wizard = FindWizard.as_view([
    ('selecrecord-find_creation', RecordFormSelectionTable),
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
    ('selecrecord-find_modification', RecordFormSelection),
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


class NewFindBasketView(IshtarMixin, LoginRequiredMixin, CreateView):
    template_name = 'ishtar/form.html'
    model = models.FindBasket
    form_class = NewFindBasketForm
    page_name = _(u"New basket")

    def get_form_kwargs(self):
        kwargs = super(NewFindBasketView, self).get_form_kwargs()
        kwargs['user'] = IshtarUser.objects.get(pk=self.request.user.pk)
        return kwargs

    def get_success_url(self):
        return reverse('select_itemsinbasket',
                       kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


class SelectBasketForManagement(IshtarMixin, LoginRequiredMixin, FormView):
    template_name = 'ishtar/form.html'
    form_class = SelectFindBasketForm
    page_name = _(u"Manage items in basket")

    def get_form_kwargs(self):
        kwargs = super(SelectBasketForManagement, self).get_form_kwargs()
        kwargs['user'] = IshtarUser.objects.get(pk=self.request.user.pk)
        if 'pk' in self.kwargs:
            kwargs['initial'].update({'basket': self.kwargs['pk']})
        return kwargs

    def get_success_url(self, basket):
        return reverse('select_itemsinbasket',
                       kwargs={'pk': basket})

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url(
            form.cleaned_data['basket']))


class SelectItemsInBasket(IshtarMixin, LoginRequiredMixin, TemplateView):
    template_name = 'ishtar/manage_basket.html'
    page_name = _(u"Manage basket")

    def get_context_data(self, *args, **kwargs):
        context = super(SelectItemsInBasket, self).get_context_data(
            *args, **kwargs)
        self.user = IshtarUser.objects.get(pk=self.request.user.pk)
        try:
            self.basket = models.FindBasket.objects.get(
                pk=self.kwargs['pk'], user=self.user)
        except models.FindBasket.DoesNotExist:
            raise PermissionDenied
        context['basket'] = self.basket
        context['form'] = MultipleFindFormSelection()
        context['add_url'] = reverse('add_iteminbasket')
        context['list_url'] = reverse('list_iteminbasket',
                                      kwargs={'pk': self.basket.pk})
        return context

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url())


class FindBasketAddItemView(IshtarMixin, LoginRequiredMixin, FormView):
    template_name = 'ishtar/simple_form.html'
    form_class = FindBasketAddItemForm

    def get_success_url(self, basket):
        return reverse('list_iteminbasket', kwargs={'pk': basket.pk})

    def form_valid(self, form):
        user = IshtarUser.objects.get(pk=self.request.user.pk)
        # rights are checked on the form
        basket = form.save(user)
        return HttpResponseRedirect(self.get_success_url(basket))


class FindBasketListView(IshtarMixin, LoginRequiredMixin, TemplateView):
    template_name = 'ishtar/basket_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(FindBasketListView, self).get_context_data(
            *args, **kwargs)
        self.user = IshtarUser.objects.get(pk=self.request.user.pk)
        try:
            self.basket = models.FindBasket.objects.get(
                pk=self.kwargs['pk'], user=self.user)
        except models.FindBasket.DoesNotExist:
            raise PermissionDenied
        context['basket'] = self.basket
        context['item_url'] = '/'.join(
            reverse(models.Find.SHOW_URL, args=[1]).split('/')[:-1])
        context['delete_url'] = '/'.join(
            reverse('delete_iteminbasket', args=[1, 1]).split('/')[:-3])
        return context


class FindBasketDeleteItemView(IshtarMixin, LoginRequiredMixin, TemplateView):
    template_name = 'ishtar/simple_form.html'

    def get_success_url(self, basket):
        return reverse('list_iteminbasket', kwargs={'pk': basket.pk})

    def get(self, *args, **kwargs):
        user = self.request.user
        ishtaruser = IshtarUser.objects.get(pk=self.request.user.pk)
        try:
            find = models.Find.objects.get(
                pk=self.kwargs['find_pk'])
        except models.Find.DoesNotExist:
            raise PermissionDenied
        try:
            basket = models.FindBasket.objects.get(
                pk=self.kwargs['basket'], user=ishtaruser)
        except models.FindBasket.DoesNotExist:
            raise PermissionDenied
        if not user.is_superuser and \
                not ishtaruser.has_right('change_find') and \
                not (ishtaruser.has_right('change_own_find')
                     and find.is_own(user)):
            raise PermissionDenied
        basket.items.remove(find)
        return HttpResponseRedirect(self.get_success_url(basket))


class DeleteFindBasketView(IshtarMixin, LoginRequiredMixin, FormView):
    template_name = 'ishtar/form_delete.html'
    form_class = DeleteFindBasketForm
    success_url = '/'
    page_name = _(u"Delete basket")

    def get_form_kwargs(self):
        kwargs = super(DeleteFindBasketView, self).get_form_kwargs()
        kwargs['user'] = IshtarUser.objects.get(pk=self.request.user.pk)
        return kwargs

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(self.get_success_url())

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
