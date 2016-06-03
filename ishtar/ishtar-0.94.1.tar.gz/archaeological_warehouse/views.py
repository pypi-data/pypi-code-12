#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2012  Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

import json

from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from ishtar_common.views import get_item, new_item
import models
from wizards import *
from ishtar_common.forms import FinalForm
from forms import *

get_container = get_item(
    models.Container,
    'get_container', 'container',
    extra_request_keys={
        'location': 'location__pk',
        'container_type': 'container_type__pk',
        'reference': 'reference__icontains',
    })

new_warehouse = new_item(models.Warehouse, WarehouseForm)
new_container = new_item(models.Container, ContainerForm)


def autocomplete_warehouse(request):
    if not request.user.has_perm('ishtar_common.view_warehouse',
                                 models.Warehouse)\
       and not request.user.has_perm(
            'ishtar_common.view_own_warehouse', models.Warehouse):
        return HttpResponse(mimetype='text/plain')
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    query = Q()
    for q in q.split(' '):
        extra = Q(name__icontains=q) | \
            Q(warehouse_type__label__icontains=q)
        query = query & extra
    limit = 15
    warehouses = models.Warehouse.objects.filter(query)[:limit]
    data = json.dumps([{'id': warehouse.pk, 'value': unicode(warehouse)}
                       for warehouse in warehouses])
    return HttpResponse(data, mimetype='text/plain')


def autocomplete_container(request):
    if not request.user.has_perm('ishtar_common.view_warehouse',
                                 models.Warehouse)\
       and not request.user.has_perm(
            'ishtar_common.view_own_warehouse', models.Warehouse):
        return HttpResponse(mimetype='text/plain')
    if not request.GET.get('term'):
        return HttpResponse(mimetype='text/plain')
    q = request.GET.get('term')
    query = Q()
    for q in q.split(' '):
        extra = Q(container_type__label__icontains=q) | \
            Q(container_type__reference__icontains=q) | \
            Q(reference__icontains=q) | \
            Q(location__name=q) | \
            Q(location__town=q)
        query = query & extra
    limit = 15
    containers = models.Container.objects.filter(query)[:limit]
    data = json.dumps([{'id': container.pk, 'value': unicode(container)}
                       for container in containers])
    return HttpResponse(data, mimetype='text/plain')

warehouse_packaging_wizard = PackagingWizard.as_view([
    ('seleccontainer-packaging', ContainerFormSelection),
    ('base-packaging', BasePackagingForm),
    ('multiselecitems-packaging', FindPackagingFormSelection),
    ('final-packaging', FinalForm)],
    label=_(u"Packaging"),
    url_name='warehouse_packaging',)

"""
warehouse_packaging_wizard = ItemSourceWizard.as_view([
         ('selec-warehouse_packaging', ItemsSelection),
         ('final-warehouse_packaging', FinalForm)],
          url_name='warehouse_packaging',)
"""
