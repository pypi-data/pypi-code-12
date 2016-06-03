#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import sys

from django.conf import settings
from django.db.models import Q

from ishtar_common.models import Town, Department

def load_towns():
    from geodjangofla.models import Commune
    q = None
    for dpt_number in settings.ISHTAR_DPTS:
        query = Q(insee_com__istartswith=dpt_number)
        if q:
            q = q | query
        else:
            q = query
    if q:
        q = Commune.objects.filter(q)
    else:
        q = Commune.objects
    nb, updated = 0, 0
    for town in q.all():
        surface = town.superficie or 0
        surface = surface * 10000
        defaults = {'name':town.nom_comm, 'surface':surface,
                    'center':town.centroid}
        town, created = Town.objects.get_or_create(numero_insee=town.insee_com,
                                   defaults=defaults)
        if created:
            nb += 1
        else:
            updated += 1
            for k in defaults:
                setattr(town, k, defaults[k])
            town.save()
    return nb, updated

def update_towns():
    nb, updated = 0, 0
    dpts = dict([(dpt.number, dpt) for dpt in Department.objects.all()])
    q = Town.objects.filter(numero_insee__isnull=False)
    total = q.count()
    for idx, town in enumerate(q.all()):
        sys.stdout.write('\rProcessing... %s/%d' % (
                                str(idx+1).zfill(len(str(total))), total))
        if len(town.numero_insee) < 2:
            continue
        dpt_code = town.numero_insee[:2]
        if dpt_code.startswith('9') and int(dpt_code) > 95:
            dpt_code = town.numero_insee[:3]
        if dpt_code not in dpts:
            sys.stdout.write('Missing department with INSEE code: %s' % dpt_code)
            continue
        if town.departement == dpts[dpt_code]:
            continue
        if town.departement:
            updated += 1
        else:
            nb += 1
        town.departement = dpts[dpt_code]
        town.save()
    sys.stdout.write('\n')
    return nb, updated
