#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.db.models.signals import post_delete
from django.utils.translation import ugettext_lazy as _, ugettext, pgettext

from ishtar_common.models import GeneralType, BaseHistorizedItem, \
    HistoricalRecords, OwnPerms, ShortMenuItem, Source, GeneralRelationType,\
    GeneralRecordRelations, post_delete_record_relation
from archaeological_operations.models import Operation, Period, Parcel


class DatingType(GeneralType):
    class Meta:
        verbose_name = _(u"Dating type")
        verbose_name_plural = _(u"Dating types")
        ordering = ('label',)


class DatingQuality(GeneralType):
    class Meta:
        verbose_name = _(u"Dating quality")
        verbose_name_plural = _(u"Dating qualities")
        ordering = ('label',)


class Dating(models.Model):
    period = models.ForeignKey(Period, verbose_name=_(u"Period"))
    start_date = models.IntegerField(_(u"Start date"), blank=True, null=True)
    end_date = models.IntegerField(_(u"End date"), blank=True, null=True)
    dating_type = models.ForeignKey(DatingType, verbose_name=_(u"Dating type"),
                                    blank=True, null=True)
    quality = models.ForeignKey(DatingQuality, verbose_name=_(u"Quality"),
                                blank=True, null=True)
    precise_dating = models.TextField(_(u"Precise dating"), blank=True,
                                      null=True)

    class Meta:
        verbose_name = _(u"Dating")
        verbose_name_plural = _(u"Datings")

    def __unicode__(self):
        start_date = self.start_date and unicode(self.start_date) or u""
        end_date = self.end_date and unicode(self.end_date) or u""
        if not start_date and not end_date:
            return unicode(self.period)
        return u"%s (%s-%s)" % (self.period, start_date, end_date)


class Unit(GeneralType):
    order = models.IntegerField(_(u"Order"))
    parent = models.ForeignKey("Unit", verbose_name=_(u"Parent unit"),
                               blank=True, null=True)

    class Meta:
        verbose_name = _(u"Unit Type")
        verbose_name_plural = _(u"Unit Types")
        ordering = ('order',)

    def __unicode__(self):
        return self.label


class ActivityType(GeneralType):
    order = models.IntegerField(_(u"Order"))

    class Meta:
        verbose_name = _(u"Activity Type")
        verbose_name_plural = _(u"Activity Types")
        ordering = ('order',)

    def __unicode__(self):
        return self.label


class IdentificationType(GeneralType):
    order = models.IntegerField(_(u"Order"))

    class Meta:
        verbose_name = _(u"Identification Type")
        verbose_name_plural = _(u"Identification Types")
        ordering = ('order',)

    def __unicode__(self):
        return self.label


class ContextRecord(BaseHistorizedItem, OwnPerms, ShortMenuItem):
    SHOW_URL = 'show-contextrecord'
    TABLE_COLS = ['parcel.town', 'operation.year',
                  'operation.operation_code',
                  'label', 'unit']
    if settings.COUNTRY == 'fr':
        TABLE_COLS.insert(1, 'operation.code_patriarche')
    TABLE_COLS_FOR_OPE = ['label', 'parcel', 'unit',
                          'datings.period', 'description']
    TABLE_COLS_FOR_OPE_LBL = {'section__parcel_number': _("Parcel")}
    external_id = models.CharField(_(u"External ID"), blank=True, null=True,
                                   max_length=120)
    parcel = models.ForeignKey(Parcel, verbose_name=_(u"Parcel"),
                               related_name='context_record')
    operation = models.ForeignKey(Operation, verbose_name=_(u"Operation"),
                                  related_name='context_record')
    label = models.CharField(_(u"ID"), max_length=200)
    description = models.TextField(_(u"Description"), blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    opening_date = models.DateField(_(u"Date d'ouverture"),
                                    blank=True, null=True)
    closing_date = models.DateField(_(u"End date"), blank=True, null=True)
    length = models.IntegerField(_(u"Length (cm)"), blank=True, null=True)
    width = models.IntegerField(_(u"Width (cm)"), blank=True, null=True)
    thickness = models.IntegerField(_(u"Thickness (cm)"), blank=True,
                                    null=True)
    depth = models.IntegerField(_(u"Depth (cm)"), blank=True, null=True)
    location = models.CharField(
        _(u"Location"), blank=True, null=True, max_length=200,
        help_text=_(u"A short description of the location of the context "
                    u"record"))
    datings = models.ManyToManyField(Dating)
    unit = models.ForeignKey(Unit, verbose_name=_(u"Unit"), related_name='+',
                             blank=True, null=True)
    has_furniture = models.NullBooleanField(_(u"Has furniture?"), blank=True,
                                            null=True)
    filling = models.TextField(_(u"Filling"), blank=True, null=True)
    interpretation = models.TextField(_(u"Interpretation"), blank=True,
                                      null=True)
    taq = models.IntegerField(
        _(u"TAQ"), blank=True, null=True,
        help_text=_(u"\"Terminus Ante Quem\" the context record can't have "
                    u"been created after this date"))
    taq_estimated = models.IntegerField(
        _(u"Estimated TAQ"), blank=True, null=True,
        help_text=_(u"Estimation of a \"Terminus Ante Quem\""))
    tpq = models.IntegerField(
        _(u"TPQ"), blank=True, null=True,
        help_text=_(u"\"Terminus Post Quem\" the context record can't have "
                    u"been created before this date"))
    tpq_estimated = models.IntegerField(
        _(u"Estimated TPQ"), blank=True, null=True,
        help_text=_(u"Estimation of a \"Terminus Post Quem\""))
    identification = models.ForeignKey(
        IdentificationType, blank=True, null=True,
        verbose_name=_(u"Identification"),)
    activity = models.ForeignKey(ActivityType, blank=True, null=True,
                                 verbose_name=_(u"Activity"),)
    related_context_records = models.ManyToManyField(
        'ContextRecord', through='RecordRelations', blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _(u"Context Record")
        verbose_name_plural = _(u"Context Record")
        permissions = (
            ("view_contextrecord", ugettext(u"Can view all Context Records")),
            ("view_own_contextrecord",
             ugettext(u"Can view own Context Record")),
            ("add_own_contextrecord",
             ugettext(u"Can add own Context Record")),
            ("change_own_contextrecord",
             ugettext(u"Can change own Context Record")),
            ("delete_own_contextrecord",
             ugettext(u"Can delete own Context Record")),
        )

    @property
    def name(self):
        return self.label or ""

    @property
    def short_class_name(self):
        return pgettext("short", u"Context record")

    def __unicode__(self):
        return self.short_label

    @property
    def short_label(self):
        return settings.JOINT.join([unicode(item) for item in [
            self.parcel, self.label] if item])

    @property
    def show_url(self):
        return reverse('show-contextrecord', args=[self.pk, ''])

    @classmethod
    def get_query_owns(cls, user):
        return Q(operation__scientist=user.ishtaruser.person) |\
            Q(operation__in_charge=user.ishtaruser.person) |\
            Q(history_creator=user)

    def full_label(self):
        return unicode(self)
        if not self.operation:
            return unicode(self)
        return self._real_label() or self._temp_label()

    def _real_label(self):
        if not self.operation.code_patriarche:
            return
        return settings.JOINT.join((unicode(self.operation.code_patriarche),
                                    self.label))

    def _temp_label(self):
        if self.operation.code_patriarche:
            return
        return settings.JOINT.join([unicode(lbl) for lbl in [
            self.operation.year, self.operation.operation_code, self.label]
            if lbl])

    @property
    def reference(self):
        if not self.operation:
            return "00"
        return self.full_label()

    def get_department(self):
        if not self.operation:
            return "00"
        return self.operation.get_department()

    def get_town_label(self):
        if not self.operation:
            return "00"
        return self.operation.get_town_label()

    @classmethod
    def get_periods(cls, slice='year', fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        if slice == 'year':
            years = set()
            for res in list(q.values('operation__start_date')):
                if res['operation__start_date']:
                    yr = res['operation__start_date'].year
                    years.add(yr)
            return list(years)
        return []

    @classmethod
    def get_by_year(cls, year, fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        return q.filter(operation__start_date__year=year)

    @classmethod
    def get_operations(cls):
        return [dct['operation__pk']
                for dct in cls.objects.values('operation__pk').distinct()]

    @classmethod
    def get_by_operation(cls, operation_id):
        return cls.objects.filter(operation__pk=operation_id)

    @classmethod
    def get_total_number(cls, fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        return q.count()

    def find_docs_q(self):
        from archaeological_finds.models import FindSource
        return FindSource.objects.filter(find__base_finds__context_record=self)


class RelationType(GeneralRelationType):
    inverse_relation = models.ForeignKey(
        'RelationType', verbose_name=_(u"Inverse relation"), blank=True,
        null=True)

    class Meta:
        verbose_name = _(u"Relation type")
        verbose_name_plural = _(u"Relation types")
        ordering = ('order',)


class RecordRelations(GeneralRecordRelations, models.Model):
    MAIN_ATTR = 'left_record'
    left_record = models.ForeignKey(ContextRecord,
                                    related_name='right_relations')
    right_record = models.ForeignKey(ContextRecord,
                                     related_name='left_relations')
    relation_type = models.ForeignKey(RelationType)

    class Meta:
        verbose_name = _(u"Record relation")
        verbose_name_plural = _(u"Record relations")

post_delete.connect(post_delete_record_relation, sender=RecordRelations)


class ContextRecordSource(Source):
    SHOW_URL = 'show-contextrecordsource'

    class Meta:
        verbose_name = _(u"Context record documentation")
        verbose_name_plural = _(u"Context record documentations")
    context_record = models.ForeignKey(
        ContextRecord, verbose_name=_(u"Context record"),
        related_name="source")

    @property
    def owner(self):
        return self.context_record
