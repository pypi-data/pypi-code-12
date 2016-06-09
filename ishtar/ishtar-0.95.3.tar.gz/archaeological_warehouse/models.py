#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _, ugettext

from ishtar_common.models import GeneralType, \
    LightHistorizedItem, OwnPerms, Address, Person


class WarehouseType(GeneralType):
    class Meta:
        verbose_name = _(u"Warehouse type")
        verbose_name_plural = _(u"Warehouse types")
        ordering = ('label',)


class Warehouse(Address, OwnPerms):
    name = models.CharField(_(u"Name"), max_length=40)
    warehouse_type = models.ForeignKey(WarehouseType,
                                       verbose_name=_(u"Warehouse type"))
    person_in_charge = models.ForeignKey(
        Person, on_delete=models.SET_NULL, related_name='warehouse_in_charge',
        verbose_name=_(u"Person in charge"), null=True, blank=True)
    comment = models.TextField(_(u"Comment"), null=True, blank=True)

    class Meta:
        verbose_name = _(u"Warehouse")
        verbose_name_plural = _(u"Warehouses")
        permissions = (
            ("view_warehouse", ugettext(u"Can view all Warehouses")),
            ("view_own_warehouse", ugettext(u"Can view own Warehouse")),
            ("add_own_warehouse", ugettext(u"Can add own Warehouse")),
            ("change_own_warehouse", ugettext(u"Can change own Warehouse")),
            ("delete_own_warehouse", ugettext(u"Can delete own Warehouse")),
        )

    def __unicode__(self):
        return u"%s (%s)" % (self.name, unicode(self.warehouse_type))


class ContainerType(GeneralType):
    length = models.IntegerField(_(u"Length (mm)"), blank=True, null=True)
    width = models.IntegerField(_(u"Width (mm)"), blank=True, null=True)
    height = models.IntegerField(_(u"Height (mm)"), blank=True, null=True)
    volume = models.IntegerField(_(u"Volume (l)"), blank=True, null=True)
    reference = models.CharField(_(u"Ref."), max_length=30)

    class Meta:
        verbose_name = _(u"Container type")
        verbose_name_plural = _(u"Container types")
        ordering = ('label',)


class Container(LightHistorizedItem):
    TABLE_COLS = ['reference', 'container_type', 'location']
    location = models.ForeignKey(Warehouse, verbose_name=_(u"Warehouse"))
    container_type = models.ForeignKey(ContainerType,
                                       verbose_name=_("Container type"))
    reference = models.CharField(_(u"Container ref."), max_length=40)
    comment = models.TextField(_(u"Comment"))

    class Meta:
        verbose_name = _(u"Container")
        verbose_name_plural = _(u"Containers")

    def __unicode__(self):
        lbl = u" - ".join((self.reference, unicode(self.container_type),
                           unicode(self.location)))
        return lbl
