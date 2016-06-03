#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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
    def save_model(self, dct, m2m, whole_associated_models, form_list,
                   return_object):
        dct = self.get_extra_model(dct, form_list)
        obj = self.get_current_saved_object()
        dct['location'] = dct['container'].location
        items = dct.pop('finds')
        treatment = Treatment(**dct)
        treatment.save()
        if not hasattr(items, '__iter__'):
            items = [items]
        for item in items:
            new = item.duplicate(self.request.user)
            item.downstream_treatment = treatment
            item.save()
            new.upstream_treatment = treatment
            new.container = dct['container']
            new.save()
        res = render_to_response('ishtar/wizard/wizard_done.html', {},
                                 context_instance=RequestContext(self.request))
        return return_object and (obj, res) or res
