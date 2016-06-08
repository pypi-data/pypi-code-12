#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.shortcuts import render_to_response
from django.template import RequestContext

from archaeological_finds.wizards import TreatmentWizard
from archaeological_finds.models import Treatment


class PackagingWizard(TreatmentWizard):

    def get_form_kwargs(self, step):
        kwargs = super(PackagingWizard, self).get_form_kwargs(step)
        if 'base-packaging' not in step:
            return kwargs
        kwargs['user'] = self.request.user
        return kwargs

    def save_model(self, dct, m2m, whole_associated_models, form_list,
                   return_object):
        dct = self.get_extra_model(dct, form_list)
        obj = self.get_current_saved_object()
        dct['location'] = dct['container'].location
        items = dct.pop('basket')
        treatment = Treatment(**dct)
        extra_args_for_new = {"container": dct['container']}
        treatment.save(items=items, user=self.request.user,
                       extra_args_for_new=extra_args_for_new)
        res = render_to_response('ishtar/wizard/wizard_done.html', {},
                                 context_instance=RequestContext(self.request))
        return return_object and (obj, res) or res
