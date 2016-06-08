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

import datetime
# from functools import wraps

from django.conf import settings
from django.contrib.formtools.wizard.views import NamedUrlWizardView, \
    normalize_name, get_storage, StepsHelper
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.images import ImageFile
from django.core.mail import send_mail
from django.db.models.fields.files import FileField
from django.db.models.fields.related import ManyToManyField
from django.http import HttpResponseRedirect
from django.forms import ValidationError
from django.shortcuts import render_to_response
from django.template import Context, RequestContext, loader
from django.utils.datastructures import MultiValueDict as BaseMultiValueDict
from django.utils.translation import ugettext_lazy as _
import models


class MultiValueDict(BaseMultiValueDict):
    def get(self, *args, **kwargs):
        v = super(MultiValueDict, self).getlist(*args, **kwargs)
        if callable(v):
            v = v()
        if type(v) in (list, tuple) and len(v) > 1:
            v = ",".join(v)
        else:
            v = super(MultiValueDict, self).get(*args, **kwargs)
        return v


def check_rights(rights=[], redirect_url='/'):
    """
    Decorator that checks the rights to access the view.
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not rights:
                return view_func(request, *args, **kwargs)
            if hasattr(request.user, 'ishtaruser'):
                if request.user.ishtaruser.has_right('administrator',
                                                     request.session):
                    kwargs['current_right'] = 'administrator'
                    return view_func(request, *args, **kwargs)
                for right in rights:
                    # be careful to put the more permissive rights first
                    # if granted it can allow more
                    if request.user.ishtaruser.has_right(right,
                                                         request.session):
                        kwargs['current_right'] = right
                        return view_func(request, *args, **kwargs)
            return HttpResponseRedirect(redirect_url)
        return _wrapped_view
    return decorator


def check_rights_condition(rights):
    """
    To be used to check in wizard condition_dict
    """
    def func(self):
        request = self.request
        if request.user.ishtaruser.has_right('administrator', request.session):
            return True
        for right in rights:
            if request.user.ishtaruser.has_right(right, request.session):
                return True
        return False
    return func


class Wizard(NamedUrlWizardView):
    model = None
    label = ''
    modification = None  # True when the wizard modify an item
    storage_name = \
        'django.contrib.formtools.wizard.storage.session.SessionStorage'
    translated_keys = ['title']
    wizard_done_template = 'ishtar/wizard/wizard_done.html'
    wizard_done_window = ''
    wizard_confirm = 'ishtar/wizard/confirm_wizard.html'
    wizard_templates = {}
    filter_owns = {}
    current_obj_slug = ''

    @staticmethod
    def _check_right(step, condition=True):
        '''Return a method to check the right for a specific step'''
        def check_right(self):
            cond = condition
            if callable(condition):
                cond = condition(self)
            if not cond:
                return False
            return True
            # TODO: to be check
            if not hasattr(self.request.user, 'ishtaruser'):
                return False
            return self.request.user.ishtaruser.has_right(
                ('administrator', step), session=self.request.session)
        return check_right

    def __init__(self, *args, **kwargs):
        """Check right for each step of the wizard"""
        super(Wizard, self).__init__(*args, **kwargs)
        for form_key in self.form_list.keys()[:-1]:
            condition = True
            if form_key in self.condition_dict:
                condition = self.condition_dict.get(form_key, True)
            cond = self._check_right(form_key, condition)
            self.condition_dict[form_key] = cond

    def dispatch(self, request, *args, **kwargs):
        self.current_right = kwargs.get('current_right', None)

        step = kwargs.get('step', None)
        # check that the current object is really owned by the current user
        if step and self.current_right and '_own_' in self.current_right:
            # reinit default dispatch of a wizard - not clean...
            self.request = request
            self.session = request.session
            self.prefix = self.get_prefix(*args, **kwargs)
            self.storage = get_storage(
                self.storage_name, self.prefix, request,
                getattr(self, 'file_storage', None))
            self.steps = StepsHelper(self)

            current_object = self.get_current_object()
            # not the fisrt step and current object is not owned
            if self.steps and self.steps.first != step and\
                    current_object and not current_object.is_own(request.user):
                self.session_reset(request, self.url_name)
                return HttpResponseRedirect('/')
            # extra filter on forms
            self.filter_owns_items = True
        else:
            self.filter_owns_items = False

        return super(Wizard, self).dispatch(request, *args, **kwargs)

    def get_prefix(self, *args, **kwargs):
        """As the class name can interfere when reused prefix with the url_name
        """
        return self.url_name + super(Wizard, self).get_prefix(*args,
                                                              **kwargs)

    def get_wizard_name(self):
        """As the class name can interfere when reused, use the url_name"""
        return self.url_name

    def get_template_names(self):
        templates = ['ishtar/wizard/default_wizard.html']
        current_step = self.steps.current
        wizard_templates = dict([
            (key % {'url_name': self.url_name}, self.wizard_templates[key])
            for key in self.wizard_templates
        ])
        if current_step in wizard_templates:
            templates = [wizard_templates[current_step]] + templates
        elif current_step == self.steps.last:
            templates = [self.wizard_confirm] + templates
        return templates

    def get_context_data(self, form, **kwargs):
        """Add previous, next and current steps to manage the wizard path"""
        context = super(Wizard, self).get_context_data(form)
        self.request.session['CURRENT_ACTION'] = self.get_wizard_name()
        step = self.steps.first
        current_step = self.steps.current
        dct = {'current_step': self.form_list[current_step],
               'wizard_label': self.label,
               'current_object': self.get_current_object(),
               'is_search': current_step.startswith('selec-')
               if current_step else False
               }
        context.update(dct)
        if step == current_step:
            return context
        previous_steps, next_steps, previous_step_counter = [], [], 0
        while step:
            if step == current_step \
               or (previous_steps and
                   previous_steps[-1] == self.form_list[step]):
                break
            previous_steps.append(self.form_list[step])
            previous_step_counter += 1
            if previous_step_counter >= len(self.steps):
                break
            step = self.steps.all[previous_step_counter]
        context.update({'previous_steps': previous_steps,
                        'previous_step_counter': previous_step_counter})
        storage = self.storage
        # if modification: show the next steps
        if self.modification:
            next_step = self.steps.first
            current_step_passed = False
            # force rechecking of conditions
            self.get_form_list()
            while next_step:
                # check if the form is initialized otherwise initialize it
                if not storage.get_step_data(next_step):
                    values = self.get_form_initial(next_step)
                    prefixed_values = MultiValueDict()
                    if not isinstance(values, list):
                        for key in values:
                            form_key = next_step + '-' + key
                            if isinstance(values, MultiValueDict):
                                prefixed_values.setlist(form_key,
                                                        values.getlist(key))
                            else:
                                prefixed_values[form_key] = values[key]
                    else:
                        for formset_idx, v in enumerate(values):
                            prefix = u"-%d-" % formset_idx
                            for key in v:
                                form_key = next_step + prefix + key
                                prefixed_values[form_key] = v[key]
                    if not prefixed_values:
                        # simulate a non empty data for form that might be
                        # valid when empty
                        prefixed_values['__non_empty_data'] = ''
                    storage.set_step_data(next_step, prefixed_values)
                if step == next_step:
                    current_step_passed = True
                elif current_step_passed:
                    next_steps.append(self.form_list[next_step])
                next_step = self.get_next_step(next_step)
        context.update({'next_steps': next_steps})
        # not last step: validation
        if current_step != self.steps.last:
            return context
        final_form_list = []
        for form_key in self.get_form_list().keys():
            form_obj = self.get_form(
                step=form_key,
                data=self.storage.get_step_data(form_key),
                files=self.storage.get_step_files(form_key))
            form_obj.is_valid()
            final_form_list.append(form_obj)
        last_form = final_form_list[-1]
        context.update({'datas': self.get_formated_datas(final_form_list)})
        if hasattr(last_form, 'confirm_msg'):
            context.update({'confirm_msg': last_form.confirm_msg})
        if hasattr(last_form, 'confirm_end_msg'):
            context.update({'confirm_end_msg': last_form.confirm_end_msg})
        return context

    def get_formated_datas(self, forms):
        """Get the data to present in the last page"""
        datas = []
        for form in forms:
            base_form = hasattr(form, 'forms') and form.forms[0] or form
            associated_models = hasattr(base_form, 'associated_models') and \
                base_form.associated_models or {}
            if not hasattr(form, 'cleaned_data') and hasattr(form, 'forms'):
                cleaned_datas = [frm.cleaned_data for frm in form.forms
                                 if frm.is_valid()]
                if not cleaned_datas:
                    continue
            elif not hasattr(form, 'cleaned_data'):
                continue
            else:
                cleaned_datas = type(form.cleaned_data) == list and \
                    form.cleaned_data or [form.cleaned_data]
            if hasattr(base_form, 'get_formated_datas'):
                datas.append((form.form_label,
                              base_form.get_formated_datas(cleaned_datas)))
                continue
            form_datas = []
            for cleaned_data in cleaned_datas:
                if not cleaned_data:
                    continue
                if form_datas:
                    form_datas.append(("", "", "spacer"))
                items = hasattr(base_form, 'fields') and \
                    base_form.fields.keyOrder or cleaned_data.keys()
                for key in items:
                    lbl = None
                    if key.startswith('hidden_'):
                        continue
                    if hasattr(base_form, 'fields') \
                            and key in base_form.fields:
                        lbl = base_form.fields[key].label
                        if hasattr(base_form, 'associated_labels') \
                           and key in base_form.associated_labels:
                            lbl = base_form.associated_labels[key]
                    if not lbl:
                        continue
                    value = cleaned_data[key]
                    if value is None or value == '':
                        continue
                    if key in self.translated_keys:
                        value = _(value)
                    if type(value) == bool:
                        if value:
                            value = _(u"Yes")
                        else:
                            value = _(u"No")
                    elif key in associated_models:
                        values = []
                        if type(value) in (tuple, list):
                            values = value
                        elif "," in unicode(value):
                            values = unicode(
                                value).strip('[').strip(']').split(",")
                        else:
                            values = [value]
                        rendered_values = []
                        for val in values:
                            item = associated_models[key].objects.get(pk=val)
                            if hasattr(item, 'short_label'):
                                value = unicode(item.short_label)
                            else:
                                value = unicode(item)
                            rendered_values.append(value)
                        value = u" ; ".join(rendered_values)
                    form_datas.append((lbl, value, ''))
            if form_datas:
                datas.append((form.form_label, form_datas))
        return datas

    def get_extra_model(self, dct, form_list):
        dct['history_modifier'] = self.request.user
        return dct

    def done(self, form_list, return_object=False, **kwargs):
        """Save to the model"""
        dct, m2m, whole_associated_models = {}, [], []
        # base_model for M2M
        for form in form_list:
            if not form.is_valid():
                return self.render(form)
            base_form = hasattr(form, 'forms') and form.forms[0] or form
            associated_models = hasattr(base_form, 'associated_models') and \
                base_form.associated_models or {}
            if hasattr(form, 'forms'):
                multi = False
                if form.forms:
                    frm = form.forms[0]
                    if hasattr(frm, 'base_model') and frm.base_model:
                        whole_associated_models.append(frm.base_model)
                    elif hasattr(frm, 'base_models') and frm.base_models:
                        whole_associated_models += frm.base_models
                    else:
                        whole_associated_models += associated_models.keys()
                    fields = frm.fields.copy()
                    if 'DELETE' in fields:
                        fields.pop('DELETE')
                    multi = len(fields) > 1
                    if multi:
                        assert hasattr(frm, 'base_model') or \
                            hasattr(frm, 'base_models'), \
                            u"Must define a base_model(s) for " + \
                            unicode(frm.__class__)
                for frm in form.forms:
                    if not frm.is_valid():
                        continue
                    vals = {}
                    if "DELETE" in frm.cleaned_data:
                        if frm.cleaned_data["DELETE"]:
                            continue
                        frm.cleaned_data.pop('DELETE')
                    for key in frm.cleaned_data:
                        value = frm.cleaned_data[key]
                        if value is None or value == '':
                            continue
                        if key in associated_models:
                            value = associated_models[key].objects.get(
                                pk=value)
                        if multi:
                            vals[key] = value
                        else:
                            m2m.append((key, value))
                    if multi and vals:
                        if hasattr(frm, 'base_models'):
                            for m in frm.base_models:
                                m2m.append((frm.base_model, m))
                        else:
                            m2m.append((frm.base_model, vals))
            elif type(form.cleaned_data) == dict:
                for key in form.cleaned_data:
                    if key.startswith('hidden_'):
                        continue
                    value = form.cleaned_data[key]
                    if key in associated_models:
                        if value:
                            model = associated_models[key]
                            if isinstance(value, unicode) \
                                    or isinstance(value, str) and "," in value:
                                value = value.split(",")
                            if isinstance(value, list) \
                                    or isinstance(value, tuple):
                                value = [model.objects.get(pk=val)
                                         for val in value if val]
                                if len(value) == 1:
                                    value = value[0]
                            else:
                                value = model.objects.get(pk=value)
                        else:
                            value = None
                    if (hasattr(form, 'base_model') and form.base_model and
                            form.base_model == key) or (
                            hasattr(form, 'base_models') and
                            key in form.base_models):
                        whole_associated_models.append(key)
                        if value:
                            vals = value
                            if type(vals) not in (list, tuple):
                                vals = [vals]
                            for val in vals:
                                m2m.append((key, val))
                    else:
                        dct[key] = value
        return self.save_model(dct, m2m, whole_associated_models, form_list,
                               return_object)

    def get_saved_model(self):
        "Permit a distinguo when saved model is not the base selected model"
        return self.model

    def get_current_saved_object(self):
        "Permit a distinguo when saved model is not the base selected model"
        return self.get_current_object()

    def save_model(self, dct, m2m, whole_associated_models, form_list,
                   return_object):
        dct = self.get_extra_model(dct, form_list)
        obj = self.get_current_saved_object()
        # manage dependant items
        other_objs = {}
        for k in dct.keys():
            if '__' not in k:
                continue
            vals = k.split('__')
            assert len(vals) == 2, \
                "Only one level of dependant item is managed"
            dependant_item, key = vals
            if dependant_item not in other_objs:
                other_objs[dependant_item] = {}
            other_objs[dependant_item][key] = dct.pop(k)
        if obj:
            for k in dct:
                if k.startswith('pk'):
                    continue
                # False set to None for images and files
                if not k.endswith('_id') and (
                   isinstance(obj.__class__._meta.get_field(k), FileField) or
                   isinstance(obj.__class__._meta.get_field(k), ImageFile)):
                    if not dct[k]:
                        dct[k] = None
                if not k.endswith('_id') and (
                   isinstance(obj.__class__._meta.get_field(k),
                              ManyToManyField)):
                    if not dct[k]:
                        dct[k] = []
                    elif type(dct[k]) not in (list, tuple):
                        dct[k] = [dct[k]]
                setattr(obj, k, dct[k])
            try:
                obj.full_clean()
            except ValidationError:
                return self.render(form_list[-1])
            for dependant_item in other_objs:
                c_item = getattr(obj, dependant_item)
                if callable(c_item):
                    c_item = c_item()
                # manage ManyToMany if only one associated
                if hasattr(c_item, "all"):
                    c_items = c_item.all()
                    if len(c_items) != 1:
                        continue
                    c_item = c_items[0]
                if c_item:
                    # to check #
                    for k in other_objs[dependant_item]:
                        setattr(c_item, k, other_objs[dependant_item][k])
                    c_item.save()
                else:
                    m = getattr(self.model, dependant_item)
                    if callable(m):
                        m = m()
                    if hasattr(m, 'related'):
                        c_item = m.related.model(**other_objs[dependant_item])
                        setattr(obj, dependant_item, c_item)
                obj.save()
            obj.save()
        else:
            adds = {}
            # manage attributes relations
            if hasattr(self.model, 'ATTRS_EQUIV'):
                for k in other_objs.keys():
                    if k in self.model.ATTRS_EQUIV:
                        new_k = self.model.ATTRS_EQUIV[k]
                        if new_k in other_objs:
                            other_objs[new_k].update(
                                other_objs[k])
                        else:
                            other_objs[new_k] = \
                                other_objs[k].copy()
            for dependant_item in other_objs:
                if hasattr(self.model, 'ATTRS_EQUIV') and \
                        dependant_item in self.model.ATTRS_EQUIV:
                    continue
                m = getattr(self.model, dependant_item)
                if callable(m):
                    m = m()
                model = m.field.rel.to
                c_dct = other_objs[dependant_item].copy()
                if issubclass(model, models.BaseHistorizedItem):
                    c_dct['history_modifier'] = self.request.user
                c_item = model(**c_dct)
                c_item.save()
                if hasattr(m, 'through'):
                    adds[dependant_item] = c_item
                elif hasattr(m, 'field'):
                    dct[dependant_item] = c_item
            if 'pk' in dct:
                dct.pop('pk')
            obj = self.get_saved_model()(**dct)
            try:
                obj.full_clean()
            except ValidationError:
                return self.render(form_list[-1])
            obj.save()
            for k in adds:
                getattr(obj, k).add(adds[k])
            # necessary to manage interaction between models like
            # material_index management for baseitems
            obj.save()
        m2m_items = {}
        # clear
        # TODO! perf - to be really optimized
        for model in whole_associated_models:
            related_model = getattr(obj, model + 's')
            # clear real m2m
            if hasattr(related_model, 'clear'):
                related_model.clear()
            else:
                for r in related_model.all():
                    r.delete()
        for key, value in m2m:
            related_model = getattr(obj, key + 's')
            if key not in m2m_items:
                if type(key) == dict:
                    vals = []
                    for item in related_model.all():
                        v = {}
                        for k in value.keys():
                            v[k] = getattr(item, k)
                        vals.append(v)
                    m2m_items[key] = vals
                else:
                    m2m_items[key] = related_model.all()
            if value not in m2m_items[key]:
                if type(value) == dict:
                    model = related_model.model
                    if issubclass(model, models.BaseHistorizedItem):
                        value['history_modifier'] = self.request.user
                    # not m2m -> foreign key
                    if not hasattr(related_model, 'clear'):
                        assert hasattr(model, 'MAIN_ATTR'), \
                            u"Must define a MAIN_ATTR for " + \
                            unicode(model.__class__)
                        value[getattr(model, 'MAIN_ATTR')] = obj
                    value = model.objects.create(**value)
                    value.save()
                # check that an item is not add multiple times (forged forms)
                if value not in related_model.all() and\
                        hasattr(related_model, 'add'):
                    related_model.add(value)
                    # necessary to manage interaction between models like
                    # material_index management for baseitems
                    obj.save()
        # make the new object a default
        if self.current_obj_slug:
            self.request.session[self.current_obj_slug] = unicode(obj.pk)
        self.request.session[self.get_object_name(obj)] = unicode(obj.pk)
        dct = {'item': obj}
        # force evaluation of lazy urls
        wizard_done_window = unicode(self.wizard_done_window)
        if wizard_done_window:
            dct['wizard_done_window'] = wizard_done_window
        res = render_to_response(self.wizard_done_template, dct,
                                 context_instance=RequestContext(self.request))
        return return_object and (obj, res) or res

    def get_deleted(self, keys):
        """Get the deleted and non-deleted items in formsets"""
        not_to_delete, to_delete = set(), set()
        for key in keys:
            items = key.split('-')
            if len(items) < 2 or items[-2] in to_delete:
                continue
            idx = items[-2]
            try:
                int(idx)
            except:
                continue
            if items[-1] == u'DELETE':
                to_delete.add(idx)
                if idx in not_to_delete:
                    not_to_delete.remove(idx)
            elif idx not in not_to_delete:
                not_to_delete.add(idx)
        return (to_delete, not_to_delete)

    def get_form(self, step=None, data=None, files=None):
        """Manage formset"""
        if data:
            data = data.copy()
            if not step:
                step = self.steps.current
            form = self.get_form_list()[step]
            if hasattr(form, 'management_form'):
                # manage deletion
                to_delete, not_to_delete = self.get_deleted(data.keys())
                # raz deleted fields
                for key in data.keys():
                    items = key.split('-')
                    if len(items) < 2 or items[-2] not in to_delete:
                        continue
                    data.pop(key)
                if to_delete:
                    # reorganize
                    for idx, number in enumerate(sorted(not_to_delete,
                                                        key=lambda x: int(x))):
                        idx = unicode(idx)
                        if idx == number:
                            continue
                        for key in data.keys():
                            items = key.split('-')
                            if len(items) > 2 and number == items[-2]:
                                items[-2] = unicode(idx)
                                k = u'-'.join(items)
                                data[k] = data.pop(key)[0]
                # get a form key
                frm = form.form
                if callable(frm):
                    frm = frm()
                required_fields = [ki for ki in frm.fields
                                   if frm.fields[ki].required]
                base_key = None
                if required_fields:
                    base_key = required_fields[-1]
                elif frm.fields.keys():
                    base_key = frm.fields.keys()[-1]
                init = self.get_form_initial(step, data=data)
                total_field = 0
                if base_key:
                    total_field = len([key for key in data.keys()
                                       if base_key in key.split('-')
                                       and data[key]])
                if init and not to_delete and (
                   not hasattr(self, 'form_initialized') or
                   not self.form_initialized):
                    total_field = max((total_field, len(init)))
                data[step + u'-INITIAL_FORMS'] = unicode(total_field)
                data[step + u'-TOTAL_FORMS'] = unicode(total_field + 1)
                # TODO:remove form_initialized?
                # update initialization
                # if request.POST and init and hasattr(self,
                #                                      'form_initialized') \
                #   and self.form_initialized:
                #    for k in init[0]:
                #        data[step + '-' + unicode(total_field) + '-' + k] = \
                #                                                      init[0][k]
        data = data or None
        form = super(Wizard, self).get_form(step, data, files)
        # add autofocus to first field
        frm = None
        if hasattr(form, 'fields') and form.fields.keys():
            frm = form
        elif hasattr(form, 'extra_form') and hasattr(form.extra_form, 'fields')\
                and form.extra_form.fields.keys():
            frm = form.extra_form
        elif hasattr(form, 'forms') and form.forms \
                and form.forms[0].fields.keys():
            frm = form.forms[0]
        if frm:
            # autofocus on first field
            first_field = frm.fields[frm.fields.keyOrder[0]]
            attrs = first_field.widget.attrs
            attrs.update({'autofocus': "autofocus"})
            first_field.widget.attrs = attrs
            if not step:
                step = self.steps.current
            if self.filter_owns_items and self.filter_owns \
                    and step in self.filter_owns:
                for key in self.filter_owns[step]:
                    frm.fields[key].widget.source = unicode(
                        frm.fields[key].widget.source) + "own/"
                    if frm.fields[key].widget.source_full is not None:
                        frm.fields[key].widget.source_full = unicode(
                            frm.fields[key].widget.source_full) + "own/"
        return form

    def render_next_step(self, form, **kwargs):
        """
        Manage:
         - modify or delete button in formset: next step = current step
         - validate and end: nextstep = last step
        """
        request = self.request
        if request.POST.get('formset_modify') \
           or request.POST.get('formset_add') \
           or [key for key in request.POST.keys()
               if key.endswith('DELETE') and request.POST[key]]:
            return self.render(form)
        elif 'validate_and_end' in request.POST \
                and request.POST['validate_and_end']:
            last_step = self.steps.last
            new_form = self.get_form(
                last_step,
                data=self.storage.get_step_data(last_step),
                files=self.storage.get_step_files(last_step))
            self.storage.current_step = last_step
            return self.render(new_form)
        return super(Wizard, self).render_next_step(form, **kwargs)

    def post(self, *args, **kwargs):
        # manage previous (or next) step
        form_prev_step = self.request.POST.get('form_prev_step', None)
        if not form_prev_step:
            return super(Wizard, self).post(*args, **kwargs)
        try:
            # convert numerical step number to step name
            step_number = int(self.request.POST['form_prev_step'])
            wizard_goto_step = self.get_form_list().keys()[step_number]
        except (ValueError, IndexError):
            return super(Wizard, self).post(*args, **kwargs)
        self.storage.current_step = wizard_goto_step
        form = self.get_form(
            data=self.storage.get_step_data(self.steps.current),
            files=self.storage.get_step_files(self.steps.current))
        return self.render(form)

    def session_get_keys(self, form_key):
        """Get list of available keys for a specific form
        """
        request = self.request
        storage = self.storage
        test = storage.prefix in request.session \
            and 'step_data' in request.session[storage.prefix] \
            and form_key in request.session[storage.prefix]['step_data']
        if not test:
            return []
        return request.session[storage.prefix]['step_data'][form_key].keys()

    def session_has_key(self, form_key, key=None, multi=None):
        """Check if the session has value of a specific form and (if provided)
        of a key
        """
        request = self.request
        storage = self.storage
        test = storage.prefix in request.session \
            and 'step_data' in request.session[storage.prefix] \
            and form_key in request.session[storage.prefix]['step_data']
        if not key or not test:
            return test
        if multi:
            # only check if the first field is available
            key = key.startswith(form_key) and key or \
                form_key + '-0-' + key
            if key in request.session[storage.prefix]['step_data'][form_key]:
                return True
        key = key.startswith(form_key) and key or \
            form_key + '-' + key
        return key in request.session[storage.prefix]['step_data'][form_key]

    @classmethod
    def session_reset(cls, request, url_name):
        prefix = url_name + normalize_name(cls.__name__)
        storage = get_storage(cls.storage_name, prefix, request,
                              getattr(cls, 'file_storage', None))
        storage.reset()

    @classmethod
    def session_set_value(cls, request, form_key, key, value, reset=False):
        prefix = form_key.split('-')[1] + normalize_name(cls.__name__)
        storage = get_storage(cls.storage_name, prefix, request,
                              getattr(cls, 'file_storage', None))
        if reset:
            storage.reset()
        data = storage.get_step_data(form_key)
        if not data:
            data = MultiValueDict()
        key = key if key.startswith(form_key) else form_key + '-' + key
        data[key] = value
        storage.set_step_data(form_key, data)

    def session_get_value(self, form_key, key, multi=False, multi_value=False):
        """Get the value of a specific form"""
        if not self.session_has_key(form_key, key, multi):
            return
        request = self.request
        storage = self.storage
        if not multi:
            key = key.startswith(form_key) and key or form_key + '-' + key
            val = request.session[storage.prefix]['step_data'][form_key][key]
            if type(val) in (list, tuple) and val:
                if multi_value:
                    return val
                val = val[0]
            elif multi_value:
                if val:
                    return [val]
                return []
            return val
        vals = []
        for k in request.session[storage.prefix]['step_data'][form_key]:
            if k.startswith(form_key) and k.endswith(key) and \
                    request.session[storage.prefix]['step_data'][form_key][k]:
                val = request.session[storage.prefix]['step_data'][form_key][k]
                number = int(k[len(form_key):-len(key)].strip('-'))
                if type(val) in (list, tuple):
                    val = val[0]
                vals.append((number, val))
        # reorder list
        vals = [v for idx, v in sorted(vals)]
        return vals

    def get_current_object(self):
        """Get the current object for an instancied wizard"""
        current_obj = None
        main_form_key = 'selec-' + self.url_name
        try:
            idx = self.session_get_value(main_form_key, 'pk')
            idx = int(idx)
            current_obj = self.model.objects.get(pk=idx)
        except(TypeError, ValueError, ObjectDoesNotExist):
            pass
        return current_obj

    def get_form_initial(self, step, data=None):
        current_obj = self.get_current_object()
        current_step = self.steps.current
        request = self.request
        if step.startswith('selec-') and step in self.form_list \
           and 'pk' in self.form_list[step].associated_models:
            model_name = self.form_list[step]\
                             .associated_models['pk'].__name__.lower()
            if step == current_step:
                self.storage.reset()
            val = model_name in request.session and request.session[model_name]
            if val:
                return MultiValueDict({'pk': val})
        elif current_obj:
            return self.get_instanced_init(current_obj, step)
        current_form = self.form_list[current_step]
        if hasattr(current_form, 'currents'):
            initial = MultiValueDict()
            for key in current_form.currents:
                model_name = current_form.currents[key].__name__.lower()
                val = model_name in request.session and \
                    request.session[model_name]
                if val:
                    initial[key] = val
            if initial:
                return initial
        return super(Wizard, self).get_form_initial(step)

    def get_object_name(self, obj):
        obj_name = obj.__class__.__name__.lower()
        # prefer a specialized name if available
        prefixes = self.storage.prefix.split('_')
        if len(prefixes) > 1 and prefixes[-2].startswith(obj_name):
            obj_name = prefixes[-2]
        return obj_name

    def get_instanced_init(self, obj, step=None):
        """Get initial data from an init"""
        current_step = step or self.steps.current
        c_form = self.form_list[current_step]
        # make the current object the default item for the session
        self.request.session[self.get_object_name(obj)] = unicode(obj.pk)
        initial = MultiValueDict()
        if self.request.POST or \
                (step in self.request.session[self.storage.prefix] and
                 self.request.session[self.storage.prefix]['step_data'][step]):
            return initial
        if hasattr(c_form, 'base_fields'):
            for base_field in c_form.base_fields.keys():
                value = obj
                base_model = None
                if hasattr(c_form, 'base_model') and \
                   base_field == c_form.base_model:
                    base_model = base_field
                if hasattr(c_form, 'base_models') and \
                   base_field in c_form.base_models:
                    base_model = base_field
                if base_model:
                    key = base_model + 's'
                    initial.setlist(base_field, [
                        unicode(val.pk) for val in getattr(value, key).all()])
                else:
                    fields = base_field.split('__')
                    for field in fields:
                        if callable(value):
                            value = value()
                        if not hasattr(value, field) or \
                                getattr(value, field) is None:
                            value = obj
                            break
                        value = getattr(value, field)
                if hasattr(value, 'all') and callable(value.all):
                    if not value.count():
                        continue
                    initial.setlist(base_field,
                                    [unicode(v.pk) for v in value.all()])
                    continue
                if value == obj:
                    continue
                if hasattr(value, 'pk'):
                    value = value.pk
                if value in (True, False) or \
                   isinstance(value, FileField) or \
                   isinstance(value, ImageFile):
                    initial[base_field] = value
                elif value is not None:
                    initial[base_field] = unicode(value)
        elif hasattr(c_form, 'management_form'):
            initial = []
            if hasattr(c_form.form, 'base_model'):
                key = c_form.form.base_model + 's'
            else:
                key = current_step.split('-')[0]
            if not hasattr(obj, key):
                return initial
            keys = c_form.form.base_fields.keys()
            query = getattr(obj, key)
            if not obj._meta.ordering:
                query = query.order_by('pk')
            for child_obj in query.all():
                if not keys:
                    break
                vals = {}
                if len(keys) == 1:
                    # only one field: must be the id of the object
                    vals[keys[0]] = unicode(child_obj.pk)
                else:
                    for field in keys:
                        if hasattr(child_obj, field):
                            value = getattr(child_obj, field)
                            if hasattr(value, 'pk'):
                                value = value.pk
                            if value is not None:
                                vals[field] = unicode(value)
                if vals:
                    initial.append(vals)
        return initial


class SearchWizard(NamedUrlWizardView):
    model = None
    label = ''
    modification = None  # True when the wizard modify an item
    storage_name = \
        'django.contrib.formtools.wizard.storage.session.SessionStorage'

    def get_wizard_name(self):
        """
        As the class name can interfere when reused, use the url_name
        """
        return self.url_name

    def get_prefix(self, *args, **kwargs):
        """As the class name can interfere when reused prefix with the url_name
        """
        return self.url_name + super(SearchWizard, self).get_prefix(*args,
                                                                    **kwargs)

    def get_template_names(self):
        templates = ['ishtar/wizard/search.html']
        return templates

    def get_context_data(self, form, **kwargs):
        context = super(SearchWizard, self).get_context_data(form)
        self.request.session['CURRENT_ACTION'] = self.get_wizard_name()
        current_step = self.steps.current
        context.update({'current_step': self.form_list[current_step],
                        'is_search': True,
                        'wizard_label': self.label})
        return context


class DeletionWizard(Wizard):
    def __init__(self, *args, **kwargs):
        if (not hasattr(self, 'fields') or not self.fields) and \
           (hasattr(self, 'model') and hasattr(self.model, 'TABLE_COLS')):
            self.fields = self.model.TABLE_COLS
        return super(DeletionWizard, self).__init__(*args, **kwargs)

    def get_formated_datas(self, forms):
        datas = super(DeletionWizard, self).get_formated_datas(forms)
        self.current_obj = None
        for form in forms:
            if not hasattr(form, "cleaned_data"):
                continue
            for key in form.cleaned_data:
                if key == 'pk':
                    model = form.associated_models['pk']
                    self.current_obj = model.objects.get(
                        pk=form.cleaned_data['pk'])
        if not self.current_obj:
            return datas
        res = {}
        for field in self.model._meta.fields + self.model._meta.many_to_many:
            if field.name not in self.fields:
                continue
            value = getattr(self.current_obj, field.name)
            if not value:
                continue
            if hasattr(value, 'all'):
                value = ", ".join([unicode(item) for item in value.all()])
                if not value:
                    continue
            else:
                value = unicode(value)
            res[field.name] = (field.verbose_name, value, '')
        if not datas and self.fields:
            datas = [['', []]]
        for field in self.fields:
            if field in res:
                datas[0][1].append(res[field])
        return datas

    def done(self, form_list, **kwargs):
        obj = self.get_current_object()
        try:
            obj.delete()
        except ObjectDoesNotExist:
            pass
        return render_to_response(
            'ishtar/wizard/wizard_delete_done.html', {},
            context_instance=RequestContext(self.request))


class ClosingWizard(Wizard):
    # "close" an item
    # to be define in the overloaded class
    model = None
    fields = []

    def get_formated_datas(self, forms):
        datas = super(ClosingWizard, self).get_formated_datas(forms)
        self.current_obj = None
        for form in forms:
            if not hasattr(form, "cleaned_data"):
                continue
            for key in form.cleaned_data:
                if key == 'pk':
                    model = form.associated_models['pk']
                    self.current_obj = model.objects.get(
                        pk=form.cleaned_data['pk'])
        if not self.current_obj:
            return datas
        res = {}
        for field in self.model._meta.fields + self.model._meta.many_to_many:
            if field.name not in self.fields:
                continue
            value = getattr(self.current_obj, field.name)
            if not value:
                continue
            if hasattr(value, 'all'):
                value = ", ".join([unicode(item) for item in value.all()])
                if not value:
                    continue
            else:
                value = unicode(value)
            res[field.name] = (field.verbose_name, value, '')
        if not datas and self.fields:
            datas = [['', []]]
        for field in self.fields:
            if field in res:
                datas[0][1].append(res[field])
        return datas

    def done(self, form_list, **kwargs):
        obj = self.get_current_object()
        for form in form_list:
            if form.is_valid():
                if 'end_date' in form.cleaned_data \
                        and hasattr(obj, 'end_date'):
                    obj.end_date = form.cleaned_data['end_date']
                    obj.save()
        return render_to_response(
            'ishtar/wizard/wizard_closing_done.html', {},
            context_instance=RequestContext(self.request))


class PersonWizard(Wizard):
    model = models.Person
    wizard_templates = {
        'identity-person_creation': "ishtar/wizard/wizard_person.html"}


class PersonModifWizard(PersonWizard):
    modification = True
    wizard_templates = {
        'identity-person_modification': "ishtar/wizard/wizard_person.html"}


class PersonDeletionWizard(DeletionWizard):
    model = models.Person
    fields = model.TABLE_COLS
    wizard_templates = {
        'final-person_deletion': 'ishtar/wizard/wizard_person_deletion.html'}


class OrganizationWizard(Wizard):
    model = models.Organization


class OrganizationModifWizard(OrganizationWizard):
    modification = True


class OrganizationDeletionWizard(DeletionWizard):
    model = models.Organization
    fields = model.TABLE_COLS
    wizard_templates = {
        'final-organization_deletion':
        'ishtar/wizard/wizard_organization_deletion.html'}


class AccountWizard(Wizard):
    model = models.Person

    def get_formated_datas(self, forms):
        datas = super(AccountWizard, self).get_formated_datas(forms)
        for form in forms:
            if not hasattr(form, "cleaned_data"):
                continue
            for key in form.cleaned_data:
                if key == 'hidden_password' and form.cleaned_data[key]:
                    datas[-1][1].append((_("New password"), "*" * 8))
        return datas

    def done(self, form_list, **kwargs):
        """
        Save the account
        """
        dct = {}
        for form in form_list:
            if not form.is_valid():
                return self.render(form)
            associated_models = hasattr(form, 'associated_models') and \
                form.associated_models or {}
            if type(form.cleaned_data) == dict:
                for key in form.cleaned_data:
                    if key == 'pk':
                        continue
                    value = form.cleaned_data[key]
                    if key in associated_models and value:
                        value = associated_models[key].objects.get(pk=value)
                    dct[key] = value
        person = self.get_current_object()
        if not person:
            return self.render(form)
        for key in dct.keys():
            if key.startswith('hidden_password'):
                dct['password'] = dct.pop(key)
        try:
            account = models.IshtarUser.objects.get(person=person)
            account.username = dct['username']
            account.email = dct['email']
        except ObjectDoesNotExist:
            now = datetime.datetime.now()
            account = models.IshtarUser(
                person=person, username=dct['username'], email=dct['email'],
                first_name=person.surname or '***',
                last_name=person.name or '***',
                is_staff=False, is_active=True, is_superuser=False,
                last_login=now, date_joined=now)
        if dct['password']:
            account.set_password(dct['password'])
        account.save()

        if 'send_password' in dct and dct['send_password'] and \
           settings.ADMINS:
            site = Site.objects.get_current()

            app_name = site and ("Ishtar - " + site.name) \
                or "Ishtar"
            context = Context({
                'login': dct['username'],
                'password': dct['password'],
                'app_name': app_name,
                'site': site and site.domain or ""
            })
            t = loader.get_template('account_activation_email.txt')
            msg = t.render(context)
            subject = _(u"[%(app_name)s] Account creation/modification") % {
                "app_name": app_name}
            send_mail(subject, msg, settings.ADMINS[0][1],
                      [dct['email']], fail_silently=True)
        res = render_to_response('ishtar/wizard/wizard_done.html', {},
                                 context_instance=RequestContext(self.request))
        return res

    def get_form(self, step=None, data=None, files=None):
        """
        Display the "Send email" field if necessary
        """
        form = super(AccountWizard, self).get_form(step, data, files)
        if not hasattr(form, 'is_hidden'):
            return form
        if self.session_get_value('account-account_management',
                                  'hidden_password'):
            form.is_hidden = False
        return form


class SourceWizard(Wizard):
    model = None

    def get_extra_model(self, dct, form_list):
        dct = super(SourceWizard, self).get_extra_model(dct, form_list)
        if 'history_modifier' in dct:
            dct.pop('history_modifier')
        return dct
