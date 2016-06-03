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

from tidylib import tidy_document as tidy

import csv
import cStringIO as StringIO
import datetime
import ho.pisa as pisa
import json
import optparse
import re
from tempfile import NamedTemporaryFile
import unicodedata

from extra_views import ModelFormSetView

from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.models import Q, ImageField
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404, HttpResponseRedirect, \
    HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext, loader
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import CreateView, DeleteView

from xhtml2odt import xhtml2odt

from menus import menu

from archaeological_files.models import File
from archaeological_context_records.models import ContextRecord
from archaeological_finds.models import Find

from archaeological_operations.forms import DashboardForm as DashboardFormOpe
from archaeological_files.forms import DashboardForm as DashboardFormFile

from ishtar_common.forms import FinalForm, FinalDeleteForm
from ishtar_common import forms_common as forms
from ishtar_common import wizards
from ishtar_common.models import HistoryError

import models

CSV_OPTIONS = {'delimiter': ';', 'quotechar': '"', 'quoting': csv.QUOTE_ALL}
ENCODING = settings.ENCODING or 'utf-8'


def index(request):
    """
    Main page
    """
    dct = {}
    try:
        return render_to_response('index.html', dct,
                                  context_instance=RequestContext(request))
    except NoReverseMatch:
        # probably rights exception (rights revoked)
        logout(request)
        return render_to_response('index.html', dct,
                                  context_instance=RequestContext(request))

person_search_wizard = wizards.SearchWizard.as_view(
    [('general-person_search', forms.PersonFormSelection)],
    label=_(u"Person search"),
    url_name='person_search',)

person_creation_wizard = wizards.PersonWizard.as_view(
    [('identity-person_creation', forms.SimplePersonForm),
     ('person_type-person_creation', forms.PersonTypeForm),
     ('final-person_creation', FinalForm)],
    label=_(u"New person"),
    url_name='person_creation')

person_modification_wizard = wizards.PersonModifWizard.as_view(
    [('selec-person_modification', forms.PersonFormSelection),
     ('identity-person_modification', forms.SimplePersonForm),
     ('person_type-person_creation', forms.PersonTypeForm),
     ('final-person_modification', FinalForm)],
    label=_(u"Person modification"),
    url_name='person_modification')


def person_modify(request, pk):
    person_modification_wizard(request)
    wizards.PersonModifWizard.session_set_value(
        request, 'selec-person_modification', 'pk', pk, reset=True)
    return redirect(reverse('person_modification',
                            kwargs={'step': 'identity-person_modification'}))


person_deletion_wizard = wizards.PersonDeletionWizard.as_view(
    [('selec-person_deletion', forms.PersonFormSelection),
     ('final-person_deletion', FinalDeleteForm)],
    label=_(u"Person deletion"),
    url_name='person_deletion',)

organization_search_wizard = wizards.SearchWizard.as_view(
    [('general-organization_search', forms.OrganizationFormSelection)],
    label=_(u"Organization search"),
    url_name='organization_search',)

organization_creation_wizard = wizards.OrganizationWizard.as_view(
    [('identity-organization_creation', forms.OrganizationForm),
     ('final-organization_creation', FinalForm)],
    label=_(u"New organization"),
    url_name='organization_creation')

organization_modification_wizard = wizards.OrganizationModifWizard.as_view(
    [('selec-organization_modification', forms.OrganizationFormSelection),
     ('identity-organization_modification', forms.OrganizationForm),
     ('final-organization_modification', FinalForm)],
    label=_(u"Organization modification"),
    url_name='organization_modification')

organization_deletion_wizard = wizards.OrganizationDeletionWizard.as_view(
    [('selec-organization_deletion', forms.OrganizationFormSelection),
     ('final-organization_deletion', FinalDeleteForm)],
    label=_(u"Organization deletion"),
    url_name='organization_deletion',)

account_management_wizard = wizards.AccountWizard.as_view(
    [('selec-account_management', forms.PersonFormSelection),
     ('account-account_management', forms.AccountForm),
     ('final-account_management', forms.FinalAccountForm)],
    label=_(u"Account management"),
    url_name='account_management',)


def get_autocomplete_generic(model, extra={'available': True}):
    def func(request):
        q = request.GET.get('term')
        query = Q(**extra)
        for q in q.split(' '):
            if not q:
                continue
            query = query & Q(label__icontains=q)
        limit = 20
        objects = model.objects.filter(query)[:limit]
        get_label = lambda x: x.full_label() if hasattr(x, 'full_label') \
            else unicode(x)
        data = json.dumps([{'id': obj.pk, 'value': get_label(obj)}
                           for obj in objects])
        return HttpResponse(data, mimetype='text/plain')
    return func


def update_current_item(request):
    if not request.is_ajax() and not request.method == 'POST':
        raise Http404
    if 'value' in request.POST and 'item' in request.POST:
        request.session[request.POST['item']] = request.POST['value']
    return HttpResponse('ok')


def check_permission(request, action_slug, obj_id=None):
    if action_slug not in menu.items:
        # TODO
        return True
    if obj_id:
        return menu.items[action_slug].is_available(request.user, obj_id,
                                                    session=request.session)
    return menu.items[action_slug].can_be_available(request.user,
                                                    session=request.session)


def autocomplete_person_permissive(request, person_types=None,
                                   attached_to=None, is_ishtar_user=None):
    return autocomplete_person(
        request, person_types=person_types, attached_to=attached_to,
        is_ishtar_user=is_ishtar_user, permissive=True)


def autocomplete_person(request, person_types=None, attached_to=None,
                        is_ishtar_user=None, permissive=False):
    if not request.user.has_perm('ishtar_common.view_person',
                                 models.Person) and \
       not request.user.has_perm('ishtar_common.view_own_person',
                                 models.Person) \
       and not request.user.ishtaruser.has_right('person_search',
                                                 session=request.session):
        return HttpResponse(mimetype='text/plain')
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    limit = request.GET.get('limit', 20)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest()
    query = Q()
    for q in q.split(' '):
        qu = (Q(name__icontains=q) | Q(surname__icontains=q) |
              Q(email__icontains=q) | Q(attached_to__name__icontains=q))
        if permissive:
            qu = qu | Q(raw_name__icontains=q)
        query = query & qu
    if attached_to:
        query = query & Q(attached_to__pk__in=attached_to.split('_'))

    if person_types and unicode(person_types) != '0':
        try:
            typs = [int(tp) for tp in person_types.split('_') if tp]
            typ = models.PersonType.objects.filter(pk__in=typs).all()
            query = query & Q(person_types__in=typ)
        except (ValueError, ObjectDoesNotExist):
            pass
    if is_ishtar_user:
        query = query & Q(ishtaruser__isnull=False)
    limit = 20
    persons = models.Person.objects.filter(query)[:limit]
    data = json.dumps([{'id': person.pk, 'value': unicode(person)}
                       for person in persons if person])
    return HttpResponse(data, mimetype='text/plain')


def autocomplete_department(request):
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    q = unicodedata.normalize("NFKD", q).encode('ascii', 'ignore')
    query = Q()
    for q in q.split(' '):
        extra = (Q(label__icontains=q) | Q(number__istartswith=q))
        query = query & extra
    limit = 20
    departments = models.Department.objects.filter(query)[:limit]
    data = json.dumps([{'id': department.pk, 'value': unicode(department)}
                       for department in departments])
    return HttpResponse(data, mimetype='text/plain')


def autocomplete_town(request):
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    q = unicodedata.normalize("NFKD", q).encode('ascii', 'ignore')
    query = Q()
    for q in q.split(' '):
        extra = Q(name__icontains=q)
        if settings.COUNTRY == 'fr':
            extra = (extra | Q(numero_insee__istartswith=q) |
                     Q(departement__label__istartswith=q))
        query = query & extra
    limit = 20
    towns = models.Town.objects.filter(query)[:limit]
    data = json.dumps([{'id': town.pk, 'value': unicode(town)}
                       for town in towns])
    return HttpResponse(data, mimetype='text/plain')


def autocomplete_advanced_town(request, department_id=None, state_id=None):
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    q = unicodedata.normalize("NFKD", q).encode('ascii', 'ignore')
    query = Q()
    for q in q.split(' '):
        extra = Q(name__icontains=q)
        if settings.COUNTRY == 'fr':
            extra = extra | Q(numero_insee__istartswith=q)
            if not department_id:
                extra = extra | Q(departement__label__istartswith=q)
        query = query & extra
    if department_id:
        query = query & Q(departement__number__iexact=department_id)
    if state_id:
        query = query & Q(departement__state__number__iexact=state_id)
    limit = 20
    towns = models.Town.objects.filter(query)[:limit]
    result = []
    for town in towns:
        val = town.name
        if hasattr(town, 'numero_insee'):
            val += " (%s)" % town.numero_insee
        result.append({'id': town.pk, 'value': val})
    data = json.dumps(result)
    return HttpResponse(data, mimetype='text/plain')


def department_by_state(request, state_id=''):
    if not state_id:
        data = []
    else:
        departments = models.Department.objects.filter(state__number=state_id)
        data = json.dumps([{'id': department.pk, 'number': department.number,
                            'value': unicode(department)}
                           for department in departments])
    return HttpResponse(data, mimetype='text/plain')


def format_val(val):
    if val is None:
        return u""
    if type(val) == bool:
        if val:
            return unicode(_(u"True"))
        else:
            return unicode(_(u"False"))
    return unicode(val)

HIERARCHIC_LEVELS = 5
HIERARCHIC_FIELDS = ['periods', 'period', 'unit', 'material_types',
                     'material_type', 'conservatory_state']
PRIVATE_FIELDS = ('id', 'history_modifier', 'order')


def get_item(model, func_name, default_name, extra_request_keys=[],
             base_request={}, bool_fields=[], reversed_bool_fields=[],
             dated_fields=[], associated_models=[], relative_session_names={},
             specific_perms=[], own_table_cols=None):
    """
    Generic treatment of tables
    """
    def func(request, data_type='json', full=False, force_own=False, **dct):
        # check rights
        own = True  # more restrictive by default
        allowed = False
        if request.user.is_authenticated() and \
                request.user.ishtaruser.has_right('administrator',
                                                  session=request.session):
            allowed = True
            own = False
        else:
            for perm, lbl in model._meta.permissions:
                # if not specific any perm is relevant (read right)
                if specific_perms and perm not in specific_perms:
                    continue
                cperm = model._meta.app_label + '.' + perm
                if request.user.has_perm(cperm)\
                        or cperm in request.user.get_all_permissions() \
                        or (request.user.is_authenticated()
                            and request.user.ishtaruser.has_right(
                                perm, session=request.session)):
                    allowed = True
                    if "_own_" not in perm:
                        own = False
                        break  # max right reach
        if force_own:
            own = True
        EMPTY = ''
        if 'type' in dct:
            data_type = dct.pop('type')
        if not data_type:
            EMPTY = '[]'
            data_type = 'json'
        if not allowed:
            return HttpResponse(EMPTY, mimetype='text/plain')
        fields = [model._meta.get_field_by_name(k)[0]
                  for k in model._meta.get_all_field_names()]
        request_keys = dict([
            (field.name,
             field.name + (hasattr(field, 'rel') and field.rel and '__pk'
                           or ''))
            for field in fields])
        for associated_model, key in associated_models:
            associated_fields = [
                associated_model._meta.get_field_by_name(k)[0]
                for k in associated_model._meta.get_all_field_names()]
            request_keys.update(
                dict([(key + "__" + field.name,
                       key + "__" + field.name +
                       (hasattr(field, 'rel') and field.rel and '__pk' or ''))
                      for field in associated_fields]))
        request_keys.update(extra_request_keys)
        request_items = request.method == 'POST' and request.POST \
            or request.GET
        dct = base_request.copy()
        and_reqs, or_reqs = [], []
        try:
            old = 'old' in request_items and int(request_items['old'])
        except ValueError:
            return HttpResponse('[]', mimetype='text/plain')

        relation_types = set()
        for k in request_items:
            if k.startswith('relation_types_'):
                relation_types.add(request_items[k])
                continue
        for k in request_keys:
            val = request_items.get(k)
            if not val:
                continue
            req_keys = request_keys[k]
            if type(req_keys) not in (list, tuple):
                dct[req_keys] = val
                continue
            # multiple choice target
            reqs = Q(**{req_keys[0]: val})
            for req_key in req_keys[1:]:
                q = Q(**{req_key: val})
                reqs = reqs | q
            and_reqs.append(reqs)
        if 'submited' not in request_items:
            if default_name in request.session and \
               request.session[default_name]:
                value = request.session[default_name]
                if 'basket-' in value:
                    dct = {"basket__pk":
                           request.session[default_name].split('-')[-1]}
                else:
                    dct = {"pk": request.session[default_name]}
            elif not dct:
                for name in relative_session_names.keys():
                    if name in request.session and request.session[name]:
                        k = relative_session_names[name]
                        dct = {k: request.session[name]}
                        break
            if (not dct or data_type == 'csv') \
                    and func_name in request.session:
                dct = request.session[func_name]
        else:
            request.session[func_name] = dct
        for k in (list(bool_fields) + list(reversed_bool_fields)):
            if k in dct:
                if dct[k] == u"1":
                    dct.pop(k)
                else:
                    dct[k] = dct[k] == u"2" and True or False
                    if k in reversed_bool_fields:
                        dct[k] = not dct[k]
                    # check also for empty value with image field
                    c_field = model._meta.get_field(k.split('__')[0])
                    if k.endswith('__isnull') and \
                       isinstance(c_field, ImageField):
                        if dct[k]:
                            or_reqs.append(
                                (k, {k.split('__')[0] + '__exact': ''}))
                        else:
                            dct[k.split('__')[0] + '__regex'] = '.{1}.*'
        for k in dated_fields:
            if k in dct:
                if not dct[k]:
                    dct.pop(k)
                try:
                    items = dct[k].split('/')
                    assert len(items) == 3
                    dct[k] = datetime.date(*map(lambda x: int(x),
                                                reversed(items)))\
                                     .strftime('%Y-%m-%d')
                except AssertionError:
                    dct.pop(k)
        # manage hierarchic conditions
        for req in dct.copy():
            for k_hr in HIERARCHIC_FIELDS:
                if type(req) in (list, tuple):
                    val = dct.pop(req)
                    q = None
                    for idx, r in enumerate(req):
                        if not idx:
                            q = Q(**{r: val})
                        else:
                            q = q | Q(**{r: val})
                    and_reqs.append(q)
                    break
                elif req.endswith(k_hr + '__pk'):
                    val = dct.pop(req)
                    reqs = Q(**{req: val})
                    req = req[:-2] + '__'
                    for idx in xrange(HIERARCHIC_LEVELS):
                        req = req[:-2] + 'parent__pk'
                        q = Q(**{req: val})
                        reqs = reqs | q
                    and_reqs.append(reqs)
                    break
        query = Q(**dct)
        for k, or_req in or_reqs:
            alt_dct = dct.copy()
            alt_dct.pop(k)
            alt_dct.update(or_req)
            query = query | Q(**alt_dct)

        if relation_types:
            alt_dct = {
                'right_relations__relation_type__pk__in': list(relation_types)}
            for k in dct:
                val = dct[k]
                if k == 'year':
                    k = 'year__exact'
                alt_dct['right_relations__right_record__' + k] = val
            if not dct:
                # fake condition to trick Django (1.4): without it only the
                # alt_dct is managed
                query = query & Q(pk__isnull=False)
            query = query | Q(**alt_dct)
            for k, or_req in or_reqs:
                altor_dct = alt_dct.copy()
                altor_dct.pop(k)
                for j in or_req:
                    val = or_req[j]
                    if j == 'year':
                        j = 'year__exact'
                    altor_dct['right_relations__right_record__' + j] = val
                query = query | Q(**altor_dct)

        if own:
            query = query & model.get_query_owns(request.user)

        for and_req in and_reqs:
            query = query & and_req

        items = model.objects.filter(query).distinct()
        q = request_items.get('sidx')

        # table cols
        if own_table_cols:
            table_cols = own_table_cols
        else:
            if full:
                table_cols = [field.name for field in model._meta.fields
                              if field.name not in PRIVATE_FIELDS]
                table_cols += [field.name for field in model._meta.many_to_many
                               if field.name not in PRIVATE_FIELDS]
                if hasattr(model, 'EXTRA_FULL_FIELDS'):
                    table_cols += model.EXTRA_FULL_FIELDS
            else:
                table_cols = model.TABLE_COLS
        # manage sort tables
        manual_sort_key = None
        order = request_items.get('sord')
        sign = order and order == u'desc' and "-" or ''
        if q and q in request_keys:
            ks = request_keys[q]
            if type(ks) not in (list, tuple):
                ks = [ks]
            orders = []
            for k in ks:
                if k.endswith("__pk"):
                    k = k[:-len("__pk")] + "__label"
                if '__' in k:
                    k = k.split('__')[0]
                orders.append(sign + k)
            items = items.order_by(*orders)
        elif q:
            for ke in table_cols:
                if type(ke) in (list, tuple):
                    ke = ke[0]
                if ke.endswith(q):
                    manual_sort_key = ke
                    break
            if not manual_sort_key and model._meta.ordering:
                orders = [sign + k for k in model._meta.ordering]
                items = items.order_by(*orders)
        # pager management
        start, end = 0, None
        page_nb = 1
        try:
            row_nb = int(request_items.get('rows'))
        except (ValueError, TypeError):
            row_nb = None
        if row_nb:
            try:
                page_nb = int(request_items.get('page'))
                assert page_nb >= 1
            except (ValueError, AssertionError):
                pass
            start = (page_nb - 1) * row_nb
            end = page_nb * row_nb
        items_nb = items.count()
        if manual_sort_key:
            items = items.all()
        else:
            items = items[start:end]

        datas = []
        if old:
            items = [item.get_previous(old) for item in items]
        c_ids = []
        for item in items:
            # manual deduplicate when distinct is not enough
            if item.pk in c_ids:
                continue
            c_ids.append(item.pk)
            data = [item.pk]
            for keys in table_cols:
                if type(keys) not in (list, tuple):
                    keys = [keys]
                my_vals = []
                for k in keys:
                    vals = [item]
                    for ky in k.split('.'):
                        new_vals = []
                        for val in vals:
                            if hasattr(val, 'all'):  # manage related objects
                                val = list(val.all())
                                for v in val:
                                    v = getattr(v, ky)
                                    if callable(v):
                                        v = v()
                                    new_vals.append(v)
                            elif val:
                                val = getattr(val, ky)
                                if callable(val):
                                    val = val()
                                new_vals.append(val)
                        vals = new_vals
                    # manage last related objects
                    if vals and hasattr(vals[0], 'all'):
                        new_vals = []
                        for val in vals:
                            new_vals += list(val.all())
                        vals = new_vals
                    if not my_vals:
                        my_vals = [format_val(va) for va in vals]
                    else:
                        new_vals = []
                        if not vals:
                            for idx, my_v in enumerate(my_vals):
                                new_vals.append(u"{}{}{}".format(
                                    my_v, u' - ', ''))
                        else:
                            for idx, v in enumerate(vals):
                                new_vals.append(u"{}{}{}".format(
                                    vals[idx], u' - ', format_val(v)))
                        my_vals = new_vals[:]
                data.append(", ".join(my_vals) or u"")
            datas.append(data)
        if manual_sort_key:
            # +1 because the id is added as a first col
            idx_col = None
            if manual_sort_key in table_cols:
                idx_col = table_cols.index(manual_sort_key) + 1
            else:
                for idx, col in enumerate(table_cols):
                    if type(col) in (list, tuple) and \
                            manual_sort_key in col:
                        idx_col = idx + 1
            if idx_col is not None:
                datas = sorted(datas, key=lambda x: x[idx_col])
                if sign == '-':
                    datas = reversed(datas)
                datas = list(datas)[start:end]
        link_template = "<a class='display_details' href='#' "\
                        "onclick='load_window(\"%%s\")'>%s</a>" % \
                        (unicode(_("Details")))
        if data_type == "json":
            rows = []
            for data in datas:
                try:
                    lnk = link_template % reverse('show-' + default_name,
                                                  args=[data[0], ''])
                except NoReverseMatch:
                    print '"show-' + default_name + "\" args (" + \
                          unicode(data[0]) + ") url not available"
                    lnk = ''
                res = {'id': data[0], 'link': lnk}
                for idx, value in enumerate(data[1:]):
                    if value:
                        table_col = table_cols[idx]
                        if type(table_col) not in (list, tuple):
                            table_col = [table_col]
                        k = "__".join([tc.split('.')[-1] for tc in table_col])
                        res[k] = value
                rows.append(res)
            data = json.dumps({
                "records": items_nb,
                "rows": rows,
                "page": page_nb,
                "total": (items_nb / row_nb + 1) if row_nb else items_nb,
            })
            return HttpResponse(data, mimetype='text/plain')
        elif data_type == "csv":
            response = HttpResponse(mimetype='text/csv')
            n = datetime.datetime.now()
            filename = u'%s_%s.csv' % (default_name,
                                       n.strftime('%Y%m%d-%H%M%S'))
            response['Content-Disposition'] = 'attachment; filename=%s'\
                                              % filename
            writer = csv.writer(response, **CSV_OPTIONS)
            col_names = []
            for field_name in table_cols:
                if hasattr(model, 'EXTRA_FULL_FIELDS_LABELS') and\
                        field_name in model.EXTRA_FULL_FIELDS_LABELS:
                    field = model.EXTRA_FULL_FIELDS_LABELS[field_name]
                    col_names.append(unicode(field).encode(ENCODING))
                    continue
                else:
                    try:
                        field = model._meta.get_field(field_name)
                    except:
                        col_names.append(u"".encode(ENCODING))
                        continue
                    col_names.append(
                        unicode(field.verbose_name).encode(ENCODING))
            writer.writerow(col_names)
            for data in datas:
                writer.writerow([val.encode(ENCODING) for val in data[1:]])
            return response
        return HttpResponse('{}', mimetype='text/plain')

    return func


def show_item(model, name, extra_dct=None):
    def func(request, pk, **dct):
        try:
            item = model.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(None)
        doc_type = 'type' in dct and dct.pop('type')
        url_name = u"/".join(reverse('show-' + name, args=['0', '']
                                     ).split('/')[:-2]) + u"/"
        dct['current_window_url'] = url_name
        date = 'date' in dct and dct.pop('date')
        dct['window_id'] = "%s-%d-%s" % (
            name, item.pk, datetime.datetime.now().strftime('%M%s'))
        if hasattr(item, 'history'):
            if date:
                try:
                    date = datetime.datetime.strptime(date,
                                                      '%Y-%m-%dT%H:%M:%S.%f')
                    item = item.get_previous(date=date)
                    assert item is not None
                except (ValueError, AssertionError):
                    return HttpResponse(None, mimetype='text/plain')
                dct['previous'] = item._previous
                dct['next'] = item._next
            else:
                historized = item.history.all()
                if historized:
                    item.history_date = historized[0].history_date
                if len(historized) > 1:
                    dct['previous'] = historized[1].history_date
        dct['item'], dct['item_name'] = item, name
        # add context
        if extra_dct:
            dct.update(extra_dct(request, item))
        context_instance = RequestContext(request)
        context_instance.update(dct)
        context_instance['output'] = 'html'
        filename = ""
        if hasattr(item, 'history_object'):
            filename = item.history_object.associated_filename
        else:
            filename = item.associated_filename
        if doc_type == "odt" and settings.ODT_TEMPLATE:
            tpl = loader.get_template('ishtar/sheet_%s.html' % name)
            context_instance['output'] = 'ODT'
            content = tpl.render(context_instance)
            try:
                tidy_options = {'output-xhtml': 1, 'indent': 1,
                                'tidy-mark': 0, 'doctype': 'auto',
                                'add-xml-decl': 1, 'wrap': 1}
                html, errors = tidy(content, options=tidy_options)
                html = html.encode('utf-8').replace("&nbsp;", "&#160;")
                html = re.sub('<pre([^>]*)>\n', '<pre\\1>', html)

                odt = NamedTemporaryFile()
                options = optparse.Values()
                options.with_network = True
                for k, v in (('input', ''),
                             ('output', odt.name),
                             ('template', settings.ODT_TEMPLATE),
                             ('with_network', True),
                             ('top_header_level', 1),
                             ('img_width', '8cm'),
                             ('img_height', '6cm'),
                             ('verbose', False),
                             ('replace_keyword', 'ODT-INSERT'),
                             ('cut_start', 'ODT-CUT-START'),
                             ('htmlid', None),
                             ('url', "#")):
                    setattr(options, k, v)
                odtfile = xhtml2odt.ODTFile(options)
                odtfile.open()
                odtfile.import_xhtml(html)
                odtfile = odtfile.save()
            except xhtml2odt.ODTExportError:
                return HttpResponse(content, content_type="application/xhtml")
            response = HttpResponse(
                mimetype='application/vnd.oasis.opendocument.text')
            response['Content-Disposition'] = 'attachment; filename=%s.odt' % \
                                              filename
            response.write(odtfile)
            return response
        elif doc_type == 'pdf':
            tpl = loader.get_template('ishtar/sheet_%s_pdf.html' % name)
            context_instance['output'] = 'PDF'
            content = tpl.render(context_instance)
            result = StringIO.StringIO()
            html = content.encode('utf-8')
            html = html.replace("<table", "<pdf:nextpage/><table repeat='1'")
            pdf = pisa.pisaDocument(StringIO.StringIO(html), result,
                                    encoding='utf-8')
            response = HttpResponse(result.getvalue(),
                                    mimetype='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s.pdf' % \
                                              filename
            if not pdf.err:
                return response
            return HttpResponse(content, content_type="application/xhtml")
        else:
            tpl = loader.get_template('ishtar/sheet_%s_window.html' % name)
            content = tpl.render(context_instance)
            return HttpResponse(content, content_type="application/xhtml")
    return func


def revert_item(model):
    def func(request, pk, date, **dct):
        try:
            item = model.objects.get(pk=pk)
            date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%f')
            item.rollback(date)
        except (ObjectDoesNotExist, ValueError, HistoryError):
            return HttpResponse(None, mimetype='text/plain')
        return HttpResponse("True", mimetype='text/plain')
    return func


def autocomplete_organization(request, orga_type=None):
    if (not request.user.has_perm('ishtar_common.view_organization',
        models.Organization) and
        not request.user.has_perm('ishtar_common.view_own_organization',
                                  models.Organization)
       and not request.user.ishtaruser.has_right(
            'person_search', session=request.session)):
        return HttpResponse(mimetype='text/plain')
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    query = Q()
    for q in q.split(' '):
        extra = Q(name__icontains=q)
        query = query & extra
    if orga_type:
        try:
            typs = [int(tp) for tp in orga_type.split('_') if tp]
            typ = models.OrganizationType.objects.filter(pk__in=typs).all()
            query = query & Q(organization_type__in=typ)
        except (ValueError, ObjectDoesNotExist):
            pass
    limit = 15
    organizations = models.Organization.objects.filter(query)[:limit]
    data = json.dumps([{'id': org.pk, 'value': unicode(org)}
                       for org in organizations])
    return HttpResponse(data, mimetype='text/plain')


def autocomplete_author(request):
    if not request.user.has_perm('ishtar_common.view_author', models.Author)\
       and not request.user.has_perm('ishtar_common.view_own_author',
                                     models.Author):
        return HttpResponse(mimetype='text/plain')
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    query = Q()
    for q in q.split(' '):
        extra = Q(person__name__icontains=q) | \
            Q(person__surname__icontains=q) | \
            Q(person__email__icontains=q) | \
            Q(author_type__label__icontains=q)
        query = query & extra
    limit = 15
    authors = models.Author.objects.filter(query)[:limit]
    data = json.dumps([{'id': author.pk, 'value': unicode(author)}
                       for author in authors])
    return HttpResponse(data, mimetype='text/plain')


def new_item(model, frm, many=False):
    def func(request, parent_name, limits=''):
        model_name = model._meta.object_name
        if not check_permission(request, 'add_' + model_name.lower()):
            not_permitted_msg = ugettext(u"Operation not permitted.")
            return HttpResponse(not_permitted_msg)
        dct = {'title': unicode(_(u'New %s' % model_name.lower())),
               'many': many}
        if request.method == 'POST':
            dct['form'] = frm(request.POST, limits=limits)
            if dct['form'].is_valid():
                new_item = dct['form'].save(request.user)
                dct['new_item_label'] = unicode(new_item)
                dct['new_item_pk'] = new_item.pk
                dct['parent_name'] = parent_name
                dct['parent_pk'] = parent_name
                if dct['parent_pk'] and '_select_' in dct['parent_pk']:
                    parents = dct['parent_pk'].split('_')
                    dct['parent_pk'] = "_".join([parents[0]] + parents[2:])
                return render_to_response(
                    'window.html', dct,
                    context_instance=RequestContext(request))
        else:
            dct['form'] = frm(limits=limits)
        return render_to_response('window.html', dct,
                                  context_instance=RequestContext(request))
    return func

new_person = new_item(models.Person, forms.PersonForm)
new_person_noorga = new_item(models.Person, forms.NoOrgaPersonForm)
new_organization = new_item(models.Organization, forms.OrganizationForm)
show_organization = show_item(models.Organization, 'organization')
get_organization = get_item(
    models.Organization,
    'get_organization', 'organization',
    extra_request_keys={
        'name': 'name__icontains',
        'organization_type': 'organization_type__pk__in',
    })
new_author = new_item(models.Author, forms.AuthorForm)
show_person = show_item(models.Person, 'person')

get_person = get_item(
    models.Person,
    'get_person', 'person',
    extra_request_keys={
        'name': ['name__icontains', 'raw_name__icontains'],
        'surname': ['surname__icontains', 'raw_name__icontains'],
        'attached_to': 'attached_to__pk',
        'person_types': 'person_types__pk__in',
    })


def action(request, action_slug, obj_id=None, *args, **kwargs):
    """
    Action management
    """
    if not check_permission(request, action_slug, obj_id):
        not_permitted_msg = ugettext(u"Operation not permitted.")
        return HttpResponse(not_permitted_msg)
    request.session['CURRENT_ACTION'] = action_slug
    dct = {}
    globals_dct = globals()
    if action_slug in globals_dct:
        return globals_dct[action_slug](request, dct, obj_id, *args, **kwargs)
    return render_to_response('index.html', dct,
                              context_instance=RequestContext(request))


def dashboard_main(request, dct, obj_id=None, *args, **kwargs):
    """
    Main dashboard
    """
    app_list = []
    profile = models.get_current_profile()
    if profile.files:
        app_list.append((_(u"Archaeological files"), 'files'))
    app_list.append((_(u"Operations"), 'operations'))
    if profile.context_record:
        app_list.append((_(u"Context records"), 'contextrecords'))
    if profile.find:
        app_list.append((_(u"Finds"), 'finds'))
    dct = {'app_list': app_list}
    return render_to_response('ishtar/dashboards/dashboard_main.html', dct,
                              context_instance=RequestContext(request))

DASHBOARD_FORMS = {}
DASHBOARD_FORMS['files'] = DashboardFormFile
DASHBOARD_FORMS['operations'] = DashboardFormOpe


def dashboard_main_detail(request, item_name):
    """
    Specific tab of the main dashboard
    """
    if item_name == 'users':
        dct = {'ishtar_users': models.UserDashboard()}
        return render_to_response(
            'ishtar/dashboards/dashboard_main_detail_users.html',
            dct, context_instance=RequestContext(request))
    form = None
    slicing, date_source, fltr, show_detail = 'year', None, {}, False
    profile = models.get_current_profile()
    if (item_name == 'files' and profile.files) \
            or item_name == 'operations':
        slicing = 'month'
    if item_name in DASHBOARD_FORMS:
        if request.method == 'POST':
            form = DASHBOARD_FORMS[item_name](request.POST)
            if form.is_valid():
                slicing = form.cleaned_data['slicing']
                fltr = form.get_filter()
                if hasattr(form, 'get_date_source'):
                    date_source = form.get_date_source()
                if hasattr(form, 'get_show_detail'):
                    show_detail = form.get_show_detail()
        else:
            form = DASHBOARD_FORMS[item_name]()
    lbl, dashboard = None, None
    if (item_name == 'files' and profile.files) \
            or item_name == 'operations':
        dashboard_kwargs = {'slice': slicing, 'fltr': fltr,
                            'show_detail': show_detail}
        # date_source is only relevant when the form has set one
        if date_source:
            dashboard_kwargs['date_source'] = date_source
    if item_name == 'files' and profile.files:
        lbl, dashboard = (_(u"Archaeological files"),
                          models.Dashboard(File, **dashboard_kwargs))
    if item_name == 'operations':
        from archaeological_operations.models import Operation
        lbl, dashboard = (_(u"Operations"),
                          models.Dashboard(Operation, **dashboard_kwargs))
    if item_name == 'contextrecords' and profile.context_record:
        lbl, dashboard = (
            _(u"Context records"),
            models.Dashboard(ContextRecord, slice=slicing, fltr=fltr))
    if item_name == 'finds' and profile.find:
        lbl, dashboard = (_(u"Finds"), models.Dashboard(Find,
                                                        slice=slicing,
                                                        fltr=fltr))
    if not lbl:
        raise Http404
    dct = {'lbl': lbl, 'dashboard': dashboard,
           'item_name': item_name.replace('-', '_'),
           'VALUE_QUOTE': '' if slicing == "year" else "'",
           'form': form, 'slicing': slicing}
    n = datetime.datetime.now()
    dct['unique_id'] = dct['item_name'] + "_" + \
        '%d_%d_%d' % (n.minute, n.second, n.microsecond)
    return render_to_response('ishtar/dashboards/dashboard_main_detail.html',
                              dct, context_instance=RequestContext(request))


def reset_wizards(request):
    # dynamicaly execute each reset_wizards of each ishtar app
    for app in settings.INSTALLED_APPS:
        if app == 'ishtar_common':
            # no need for infinite recursion
            continue
        try:
            module = __import__(app)
        except ImportError:
            continue
        if hasattr(module, 'views') and hasattr(module.views, 'reset_wizards'):
            module.views.reset_wizards(request)
    return redirect(reverse('start'))

ITEM_PER_PAGE = 20


def merge_action(model, form, key):
    def merge(request, page=1):
        current_url = key + '_merge'
        if not page:
            page = 1
        page = int(page)
        FormSet = modelformset_factory(
            model.merge_candidate.through, form=form,
            formset=forms.MergeFormSet, extra=0)
        q = model.merge_candidate.through.objects
        context = {'current_url': current_url,
                   'current_page': page,
                   'max_page': q.count() / ITEM_PER_PAGE}
        if page < context["max_page"]:
            context['next_page'] = page + 1
        if page > 1:
            context['previous_page'] = page - 1

        item_nb = page * ITEM_PER_PAGE
        item_nb_1 = item_nb + ITEM_PER_PAGE
        from_key = 'from_' + key
        to_key = 'to_' + key
        queryset = q.all().order_by(from_key + '__name')[item_nb:item_nb_1]
        FormSet.from_key = from_key
        FormSet.to_key = to_key
        if request.method == 'POST':
            context['formset'] = FormSet(request.POST, queryset=queryset)
            if context['formset'].is_valid():
                context['formset'].merge()
                return redirect(reverse(current_url, kwargs={'page': page}))
        else:
            context['formset'] = FormSet(queryset=queryset)
        return render_to_response(
            'ishtar/merge_' + key + '.html', context,
            context_instance=RequestContext(request))

    return merge

person_merge = merge_action(models.Person, forms.MergePersonForm, 'person')
organization_merge = merge_action(
    models.Organization,
    forms.MergeOrganizationForm,
    'organization'
)


class IshtarMixin(object):
    page_name = u""

    def get_context_data(self, **kwargs):
        context = super(IshtarMixin, self).get_context_data(**kwargs)
        context['page_name'] = self.page_name
        return context


class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args,
                                                        **kwargs)
        if kwargs.get('pk') and not self.request.user.is_staff and \
           not str(kwargs['pk']) == str(self.request.user.company.pk):
            return redirect(reverse('index'))
        return super(LoginRequiredMixin, self).dispatch(request, *args,
                                                        **kwargs)


class AdminLoginRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect(reverse('start'))
        return super(AdminLoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class GlobalVarEdit(IshtarMixin, AdminLoginRequiredMixin, ModelFormSetView):
    template_name = 'ishtar/formset.html'
    model = models.GlobalVar
    extra = 1
    can_delete = True
    page_name = _(u"Global variables")
    fields = ['slug', 'value', 'description']


class NewImportView(IshtarMixin, LoginRequiredMixin, CreateView):
    template_name = 'ishtar/form.html'
    model = models.Import
    form_class = forms.NewImportForm
    page_name = _(u"New import")

    def get_success_url(self):
        return reverse('current_imports')

    def form_valid(self, form):
        user = models.IshtarUser.objects.get(pk=self.request.user.pk)
        self.object = form.save(user=user)
        return HttpResponseRedirect(self.get_success_url())


class ImportListView(IshtarMixin, LoginRequiredMixin, ListView):
    template_name = 'ishtar/import_list.html'
    model = models.Import
    page_name = _(u"Current imports")
    current_url = 'current_imports'

    def get_queryset(self):
        user = models.IshtarUser.objects.get(pk=self.request.user.pk)
        return self.model.objects.filter(user=user).exclude(
            state='AC').order_by('-creation_date')

    def post(self, request, *args, **kwargs):
        for field in request.POST:
            if not field.startswith('import-action-') or \
               not request.POST[field]:
                continue
            # prevent forged forms
            try:
                imprt = models.Import.objects.get(pk=int(field.split('-')[-1]))
            except (models.Import.DoesNotExist, ValueError):
                continue
            # user can only edit his own imports
            user = models.IshtarUser.objects.get(pk=self.request.user.pk)
            if imprt.user != user:
                continue
            action = request.POST[field]
            if action == 'D':
                return HttpResponseRedirect(reverse('import_delete',
                                                    kwargs={'pk': imprt.pk}))
            elif action == 'A':
                imprt.initialize()
            elif action == 'I':
                imprt.importation()
            elif action == 'AC':
                imprt.archive()
        return HttpResponseRedirect(reverse(self.current_url))


class ImportOldListView(ImportListView):
    current_url = 'old_imports'

    def get_queryset(self):
        user = models.IshtarUser.objects.get(pk=self.request.user.pk)
        return self.model.objects.filter(
            user=user, state='AC').order_by('-creation_date')


class ImportLinkView(IshtarMixin, LoginRequiredMixin, ModelFormSetView):
    template_name = 'ishtar/formset.html'
    model = models.TargetKey
    page_name = _(u"Link unmatched items")
    extra = 0
    form_class = forms.TargetKeyForm

    def get_queryset(self):
        return self.model.objects.filter(
            is_set=False, associated_import=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('current_imports')


class ImportDeleteView(IshtarMixin, LoginRequiredMixin, DeleteView):
    template_name = 'ishtar/import_delete.html'
    model = models.Import
    page_name = _(u"Delete import")

    def get_success_url(self):
        return reverse('current_imports')


class PersonCreate(LoginRequiredMixin, CreateView):
    model = models.Person
    form_class = forms.BasePersonForm
    template_name = 'ishtar/person_form.html'

    def get_success_url(self):
        return reverse('person_edit', args=[self.object.pk])


class PersonEdit(LoginRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.BasePersonForm
    template_name = 'ishtar/person_form.html'

    def get_success_url(self):
        return reverse('person_edit', args=[self.object.pk])


class OrganizationCreate(LoginRequiredMixin, CreateView):
    model = models.Organization
    form_class = forms.BaseOrganizationForm
    template_name = 'ishtar/organization_form.html'
    form_prefix = "orga"

    def get_form_kwargs(self):
        kwargs = super(OrganizationCreate, self).get_form_kwargs()
        if hasattr(self.form_class, 'form_prefix'):
            kwargs.update({'prefix': self.form_class.form_prefix})
        return kwargs

    def get_success_url(self):
        return reverse('organization_edit', args=[self.object.pk])


class OrganizationEdit(LoginRequiredMixin, UpdateView):
    model = models.Organization
    form_class = forms.BaseOrganizationForm
    template_name = 'ishtar/organization_form.html'

    def get_form_kwargs(self):
        kwargs = super(OrganizationEdit, self).get_form_kwargs()
        if hasattr(self.form_class, 'form_prefix'):
            kwargs.update({'prefix': self.form_class.form_prefix})
        return kwargs

    def get_success_url(self):
        return reverse('organization_edit', args=[self.object.pk])


class OrganizationPersonCreate(LoginRequiredMixin, CreateView):
    model = models.Person
    form_class = forms.BaseOrganizationPersonForm
    template_name = 'ishtar/organization_person_form.html'
    relative_label = _("Corporation manager")

    def get_context_data(self, *args, **kwargs):
        data = super(OrganizationPersonCreate, self).get_context_data(*args,
                                                                      **kwargs)
        data['relative_label'] = self.relative_label
        return data

    def get_success_url(self):
        return reverse('organization_person_edit', args=[self.object.pk])


class OrganizationPersonEdit(LoginRequiredMixin, UpdateView):
    model = models.Person
    form_class = forms.BaseOrganizationPersonForm
    template_name = 'ishtar/organization_person_form.html'
    relative_label = _("Corporation manager")

    def get_context_data(self, *args, **kwargs):
        data = super(OrganizationPersonEdit, self).get_context_data(*args,
                                                                    **kwargs)
        data['relative_label'] = self.relative_label
        return data

    def get_success_url(self):
        return reverse('organization_person_edit', args=[self.object.pk])
