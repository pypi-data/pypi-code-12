#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

from django.conf import settings
from django.contrib.gis.db import models
from django.core.cache import cache
from django.db.models import Q, Count, Sum
from django.db.models.signals import post_save, m2m_changed
from django.utils.translation import ugettext_lazy as _, ugettext

from ishtar_common.utils import cached_label_changed, get_cache

from ishtar_common.models import GeneralType, BaseHistorizedItem, \
    HistoricalRecords, OwnPerms, Person, Organization, Department, Town, \
    Dashboard, DashboardFormItem, IshtarUser, ValueGetter, ShortMenuItem, \
    OperationType

from archaeological_operations.models import get_values_town_related


class FileType(GeneralType):
    class Meta:
        verbose_name = _(u"Archaeological file type")
        verbose_name_plural = _(u"Archaeological file types")
        ordering = ('label',)

    @classmethod
    def is_preventive(cls, file_type_id, key=''):
        key = key or 'preventive'
        try:
            preventive = FileType.get_cache(key).pk
            return file_type_id == preventive
        except FileType.DoesNotExist:
            return False


class PermitType(GeneralType):
    class Meta:
        verbose_name = _(u"Permit type")
        verbose_name_plural = _(u"Permit types")
        ordering = ('label',)

if settings.COUNTRY == 'fr':
    class SaisineType(GeneralType, ValueGetter):
        delay = models.IntegerField(_(u"Delay (in days)"), default=30)

        class Meta:
            verbose_name = u"Type Saisine"
            verbose_name_plural = u"Types Saisine"
            ordering = ('label',)


class File(BaseHistorizedItem, OwnPerms, ValueGetter, ShortMenuItem,
           DashboardFormItem):
    TABLE_COLS = ['numeric_reference', 'year', 'internal_reference',
                  'file_type', 'saisine_type', 'towns', ]
    year = models.IntegerField(_(u"Year"),
                               default=lambda: datetime.datetime.now().year)
    numeric_reference = models.IntegerField(
        _(u"Numeric reference"), blank=True, null=True)
    internal_reference = models.CharField(_(u"Internal reference"), blank=True,
                                          null=True, max_length=60)
    external_id = models.CharField(_(u"External ID"), blank=True, null=True,
                                   max_length=120)
    name = models.TextField(_(u"Name"), blank=True, null=True)
    file_type = models.ForeignKey(FileType, verbose_name=_(u"File type"))
    in_charge = models.ForeignKey(Person, related_name='file_responsability',
                                  verbose_name=_(u"Person in charge"),
                                  on_delete=models.SET_NULL,
                                  blank=True, null=True)
    general_contractor = models.ForeignKey(
        Person, related_name='general_contractor_files',
        verbose_name=_(u"General contractor"), blank=True, null=True,
        on_delete=models.SET_NULL,)  # aménageur - personne
    raw_general_contractor = models.CharField(_(
        u"General contractor (raw)"), max_length=200, blank=True, null=True)
    corporation_general_contractor = models.ForeignKey(
        Organization,
        related_name='general_contractor_files',
        verbose_name=_(u"General contractor organization"), blank=True,
        null=True, on_delete=models.SET_NULL,)  # aménageur
    responsible_town_planning_service = models.ForeignKey(
        Person, related_name='responsible_town_planning_service_files',
        blank=True, null=True,
        verbose_name=_(u"Responsible for town planning service"),
        on_delete=models.SET_NULL,)  # service instructeur - personne
    raw_town_planning_service = models.CharField(
        _(u"Town planning service (raw)"), max_length=200,
        blank=True, null=True)
    planning_service = models.ForeignKey(
        Organization,
        related_name='planning_service_files',
        blank=True, null=True,
        verbose_name=_(u"Town planning service organization"),
        on_delete=models.SET_NULL,)  # service instructeur
    permit_type = models.ForeignKey(
        PermitType, verbose_name=_(u"Permit type"), blank=True, null=True)
    permit_reference = models.TextField(_(u"Permit reference"), blank=True,
                                        null=True)
    end_date = models.DateField(_(u"Closing date"), null=True, blank=True)
    main_town = models.ForeignKey(Town, verbose_name=_(u"Town"), null=True,
                                  blank=True, related_name='file_main')
    towns = models.ManyToManyField(Town, verbose_name=_(u"Towns"),
                                   related_name='file')
    creation_date = models.DateField(
        _(u"Creation date"), default=datetime.date.today, blank=True,
        null=True)
    reception_date = models.DateField(_(u'Reception date'), blank=True,
                                      null=True)
    related_file = models.ForeignKey("File", verbose_name=_(u"Related file"),
                                     blank=True, null=True)
    if settings.COUNTRY == 'fr':
        saisine_type = models.ForeignKey(
            SaisineType, blank=True, null=True,
            verbose_name=u"Type de saisine")
        instruction_deadline = models.DateField(_(u'Instruction deadline'),
                                                blank=True, null=True)
    total_surface = models.IntegerField(_(u"Total surface (m2)"),
                                        blank=True, null=True)
    total_developed_surface = models.IntegerField(
        _(u"Total developed surface (m2)"), blank=True, null=True)
    locality = models.CharField(_(u"Locality"),
                                max_length=100, null=True, blank=True)
    address = models.TextField(_(u"Main address"), null=True, blank=True)
    postal_code = models.CharField(_(u"Main address - postal code"),
                                   max_length=10, null=True, blank=True)
    comment = models.TextField(_(u"Comment"), null=True, blank=True)
    # research archaeology -->
    departments = models.ManyToManyField(
        Department, verbose_name=_(u"Departments"), null=True, blank=True)
    requested_operation_type = models.ForeignKey(
        OperationType, related_name='+', null=True,
        blank=True, verbose_name=_(u"Requested operation type"))
    organization = models.ForeignKey(
        Organization, blank=True, null=True, verbose_name=_(u"Organization"),
        related_name='files', on_delete=models.SET_NULL)
    scientist = models.ForeignKey(
        Person, blank=True, null=True, related_name='scientist',
        on_delete=models.SET_NULL, verbose_name=_(u"Scientist in charge"))
    research_comment = models.TextField(_(u"Research archaeology comment"),
                                        null=True, blank=True)
    classified_area = models.NullBooleanField(
        _(u"Classified area"), blank=True, null=True)
    protected_area = models.NullBooleanField(
        _(u"Protected area"), blank=True, null=True)
    if settings.COUNTRY == 'fr':
        cira_advised = models.NullBooleanField(
            u"Passage en CIRA", blank=True, null=True)
        mh_register = models.NullBooleanField(
            u"Sur Monument Historique classé", blank=True, null=True)
        mh_listing = models.NullBooleanField(
            u"Sur Monument Historique inscrit", blank=True, null=True)
    # <-- research archaeology
    cached_label = models.TextField(_(u"Cached name"), null=True, blank=True)
    imported_line = models.TextField(_(u"Imported line"), null=True,
                                     blank=True)
    history = HistoricalRecords()

    GET_VALUES_EXTRA = [
        'general_contractor_address_1',
        'general_contractor_address_2',
        'general_contractor_address_3',
        'get_locality',
    ]

    class Meta:
        verbose_name = _(u"Archaeological file")
        verbose_name_plural = _(u"Archaeological files")
        permissions = (
            ("view_file", ugettext(u"Can view all Archaelogical files")),
            ("view_own_file", ugettext(u"Can view own Archaelogical file")),
            ("add_own_file", ugettext(u"Can add own Archaelogical file")),
            ("change_own_file",
             ugettext(u"Can change own Archaelogical file")),
            ("delete_own_file",
             ugettext(u"Can delete own Archaelogical file")),
            ("close_file", ugettext(u"Can close File")),
        )
        ordering = ('cached_label',)

    @property
    def short_class_name(self):
        return _(u"FILE")

    @property
    def delay_date(self):
        cache_key, val = get_cache(self.__class__, [self.pk, 'delay_date'])
        if val:
            return val
        return self.update_delay_date(cache_key)

    def update_delay_date(self, cache_key=None):
        if not cache_key:
            cache_key, val = get_cache(self.__class__,
                                       [self.pk, 'delay_date'])
        date = self.reception_date
        if not date:
            date = datetime.date(2500, 1, 1)
        elif settings.COUNTRY == 'fr' and self.saisine_type \
                and self.saisine_type.delay:
            date += datetime.timedelta(days=self.saisine_type.delay)
        cache.set(cache_key, date, settings.CACHE_TIMEOUT)
        return date

    @property
    def has_adminact(self):
        cache_key, val = get_cache(self.__class__, [self.pk,
                                                    'has_adminact'])
        if val:
            return val
        return self.update_has_admin_act(cache_key)

    @property
    def get_locality(self):
        return " - ".join(
            [getattr(self, k) for k in ('locality', 'address')
             if getattr(self, k)])

    @property
    def general_contractor_address_1(self):
        address = ''
        if self.general_contractor:
            if self.general_contractor.name:
                address = u" ".join([
                    getattr(self.general_contractor, key)
                    for key in ('title', 'surname', 'name')
                    if getattr(self.general_contractor, key)])
            elif self.general_contractor.raw_name:
                address = self.general_contractor.raw_name
        if not address and self.corporation_general_contractor and\
                self.corporation_general_contractor.name:
            address = self.corporation_general_contractor.name
        return address

    @property
    def general_contractor_address_2(self):
        address = ''
        if self.general_contractor and self.general_contractor.address:
            address = self.general_contractor.address
            if self.general_contractor.address_complement:
                address += u" " + self.general_contractor.address_complement
        if not address and self.corporation_general_contractor and\
                self.corporation_general_contractor.address:
            address = self.corporation_general_contractor.address
            if self.corporation_general_contractor.address_complement:
                address += u" " + \
                    self.corporation_general_contractor.address_complement
        return address

    @property
    def general_contractor_address_3(self):
        address = ''
        if self.general_contractor and self.general_contractor.postal_code:
            address = u" ".join([
                getattr(self.general_contractor, key)
                for key in ('postal_code', 'town')
                if getattr(self.general_contractor, key)])
        if not address and self.corporation_general_contractor and\
                self.corporation_general_contractor.address:
            address = u" ".join([
                getattr(self.corporation_general_contractor, key)
                for key in ('postal_code', 'town')
                if getattr(self.corporation_general_contractor, key)])
        return address

    @classmethod
    def similar_files(cls, parcels):
        # get similar parcels
        similar = set()
        for parcel in parcels:
            q = cls.objects.filter(
                parcels__town__pk=parcel['town'],
                parcels__section=parcel['section'],
                parcels__parcel_number=parcel['parcel_number']
            )
            if q.count():
                for fle in q.all():
                    similar.add(fle)
        return similar

    def update_has_admin_act(self, cache_key=None):
        if not cache_key:
            cache_key, val = get_cache(self.__class__, [self.pk,
                                                        'has_adminact'])
        has_adminact = self.administrative_act.exclude(
            act_type__txt_idx='a_receipt').count() or self.operations.count()
        cache.set(cache_key, has_adminact, settings.CACHE_TIMEOUT)
        return has_adminact

    def get_short_menu_class(self):
        cache_key, val = get_cache(self.__class__, [self.pk,
                                                    'short_class_name'])
        if val:
            return val
        return self.update_short_menu_class(cache_key)

    def update_short_menu_class(self, cache_key=None):
        if not cache_key:
            cache_key, val = get_cache(self.__class__, [self.pk,
                                                        'short_class_name'])
        cls = 'normal'
        if not self.has_adminact and self.reception_date:
            delta = datetime.date.today() - self.reception_date
            cls = 'red'
            if self.saisine_type and self.saisine_type.delay:
                if delta.days <= (self.saisine_type.delay * 2 / 3):
                    cls = 'green'
                elif delta.days <= self.saisine_type.delay:
                    cls = 'orange'
        cache.set(cache_key, cls, settings.CACHE_TIMEOUT)
        return cls

    @classmethod
    def get_owns(cls, user):
        owns = super(File, cls).get_owns(user)
        return sorted(owns, key=lambda x: x.cached_label)

    def get_values(self, prefix=''):
        values = super(File, self).get_values(prefix=prefix)
        return get_values_town_related(self, prefix, values)

    def render_parcels(self):
        from archaeological_operations.models import Parcel
        return Parcel.render_parcels(list(self.parcels.all()))

    def __unicode__(self):
        if self.cached_label:
            return self.cached_label
        self.save()
        return self.cached_label

    @property
    def short_label(self):
        return settings.JOINT.join(unicode(self).split(settings.JOINT)[1:])

    @property
    def reference(self):
        return settings.FILE_PREFIX + u"-".join(
            (unicode(self.year), unicode(self.numeric_reference or '0')))

    def _generate_cached_label(self):
        items = [self.get_town_label(), self.reference]
        items += [unicode(getattr(self, k))
                  for k in ['internal_reference', 'name'] if getattr(self, k)]
        return settings.JOINT.join(items)

    def grouped_parcels(self):
        from archaeological_operations.models import Parcel
        return Parcel.grouped_parcels(list(self.parcels.all()))

    def get_town_label(self):
        lbl = unicode(_(u'Multi-town'))
        if self.main_town:
            lbl = self.main_town.name
        elif self.towns.count() == 1:
            lbl = self.towns.all()[0].name
        elif self.towns.count() == 0:
            lbl = unicode(_(u"No town"))
        return lbl

    def get_department(self):
        if not self.towns.count():
            return '00'
        return self.towns.all()[0].numero_insee[:2]

    @classmethod
    def get_query_owns(cls, user):
        return (Q(history_creator=user) |
                Q(in_charge__ishtaruser=user.ishtaruser)) \
            & Q(end_date__isnull=True)

    def is_active(self):
        return not bool(self.end_date)

    @property
    def town_list(self):
        return u", ".join([unicode(tw) for tw in self.towns.all()])

    def closing(self):
        if self.is_active():
            return
        q = self.history
        if not q.count():
            return {'date': None, 'user': None}
        for item in q.all():
            if not item.end_date:
                break
        return {'date': item.history_date,
                'user': IshtarUser.objects.get(pk=item.history_modifier_id)}

    def total_surface_ha(self):
        if self.total_surface:
            return self.total_surface / 10000.0

    def total_developed_surface_ha(self):
        if self.total_developed_surface:
            return self.total_developed_surface / 10000.0

    def operation_acts(self):
        acts = []
        for ope in self.operations.all():
            for act in ope.administrative_act.all():
                acts.append(act)
        return acts

    def update_raw_town_planning_service(self):
        if (self.raw_town_planning_service and not
            self.responsible_town_planning_service) or \
           not self.responsible_town_planning_service:
            return False
        current_lbl = ""
        if self.raw_town_planning_service:
            current_lbl = self.raw_town_planning_service[:]
        lbl = unicode(self.responsible_town_planning_service)
        if not lbl:
            return False
        self.raw_town_planning_service = lbl[:200]
        return current_lbl != self.raw_town_planning_service

    def update_planning_service(self):
        if not self.responsible_town_planning_service or \
           not self.responsible_town_planning_service.attached_to or \
           self.planning_service:
            return False
        self.planning_service = \
            self.responsible_town_planning_service.attached_to
        return True

    def update_resp_planning_service(self):
        if not self.responsible_town_planning_service or \
           self.responsible_town_planning_service.attached_to or \
           not self.planning_service:
            return False
        self.responsible_town_planning_service.attached_to = \
            self.planning_service
        self.responsible_town_planning_service.save()
        return True

    def update_raw_general_contractor(self):
        if (self.raw_general_contractor and not
           self.general_contractor) or \
           not self.general_contractor:
            return False
        current_lbl = ""
        if self.raw_general_contractor:
            current_lbl = self.raw_general_contractor[:]
        lbl = unicode(self.general_contractor)
        if not lbl:
            return False
        self.raw_general_contractor = lbl[:200]
        return current_lbl != self.raw_general_contractor

    def update_corpo_general_contractor(self):
        if not self.general_contractor or \
           self.general_contractor.attached_to \
           == self.corporation_general_contractor:
            return False
        if self.general_contractor.attached_to:
            self.corporation_general_contractor = \
                self.general_contractor.attached_to
        else:
            self.general_contractor.attached_to = \
                self.corporation_general_contractor
            self.general_contractor.save()
        return True

    def save(self, *args, **kwargs):
        returned = super(File, self).save(*args, **kwargs)
        if self.main_town and self.main_town not in list(self.towns.all()):
            self.towns.add(self.main_town)
        updated = self.update_raw_town_planning_service()
        updated += self.update_planning_service()
        self.update_resp_planning_service()
        updated += self.update_raw_general_contractor()
        updated += self.update_corpo_general_contractor()
        if self.year and self.numeric_reference:
            external_id = u"{}{}-{}".format(settings.ISHTAR_LOCAL_PREFIX,
                                            self.year, self.numeric_reference)
            if external_id != self.external_id:
                updated = True
                self.external_id = external_id
        if updated:
            self.save()
        self.update_delay_date()
        self.update_short_menu_class()
        return returned

    def is_preventive(self):
        return FileType.is_preventive(self.file_type.pk)

m2m_changed.connect(cached_label_changed, sender=File.towns.through)
post_save.connect(cached_label_changed, sender=File)


class FileByDepartment(models.Model):
    '''
    Database view for dashboard
    '''
    file = models.ForeignKey(File, verbose_name=_(u"File"))
    department = models.ForeignKey(Department, verbose_name=_(u"Department"),
                                   blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'file_department'

    def __unicode__(self):
        return u"{} - {}".format(self.file, self.department)


class FileDashboard:
    def __init__(self):
        from archaeological_operations.models import AdministrativeAct
        main_dashboard = Dashboard(File)

        self.total_number = main_dashboard.total_number

        types = File.objects.values('file_type', 'file_type__label')
        self.types = types.annotate(number=Count('pk')).order_by('file_type')

        by_year = File.objects.extra(
            {'date': "date_trunc('year', creation_date)"})
        self.by_year = by_year.values('date')\
                              .annotate(number=Count('pk')).order_by('-date')

        now = datetime.date.today()
        limit = datetime.date(now.year, now.month, 1) - datetime.timedelta(365)
        by_month = File.objects.filter(creation_date__gt=limit).extra(
            {'date': "date_trunc('month', creation_date)"})
        self.by_month = by_month.values('date')\
                                .annotate(number=Count('pk')).order_by('-date')

        # research
        self.research = {}
        prog_type = FileType.objects.get(txt_idx='prog')
        researchs = File.objects.filter(file_type=prog_type)
        self.research['total_number'] = researchs.count()
        by_year = researchs.extra(
            {'date': "date_trunc('year', creation_date)"}
        )
        self.research['by_year'] = by_year.values('date')\
                                          .annotate(number=Count('pk'))\
                                          .order_by('-date')
        by_month = researchs.filter(creation_date__gt=limit)\
            .extra({'date': "date_trunc('month', creation_date)"})
        self.research['by_month'] = by_month.values('date')\
                                            .annotate(number=Count('pk'))\
                                            .order_by('-date')

        self.research['by_dpt'] = FileByDepartment.objects\
            .filter(file__file_type=prog_type, department__isnull=False)\
            .values('department__label')\
            .annotate(number=Count('file'))\
            .order_by('department__label')
        FileTown = File.towns.through
        self.research['towns'] = FileTown.objects\
            .filter(file__file_type=prog_type)\
            .values('town__name')\
            .annotate(number=Count('file'))\
            .order_by('-number', 'town__name')[:10]

        # rescue
        rescue_type = FileType.objects.get(txt_idx='preventive')
        rescues = File.objects.filter(file_type=rescue_type)
        self.rescue = {}
        self.rescue['total_number'] = rescues.count()
        self.rescue['saisine'] = rescues.values('saisine_type__label')\
            .annotate(number=Count('pk')).order_by('saisine_type__label')
        self.rescue['administrative_act'] = AdministrativeAct.objects\
            .filter(associated_file__isnull=False)\
            .values('act_type__label')\
            .annotate(number=Count('pk'))\
            .order_by('act_type__pk')

        by_year = rescues.extra({'date': "date_trunc('year', creation_date)"})
        self.rescue['by_year'] = by_year.values('date')\
            .annotate(number=Count('pk')).order_by('-date')
        by_month = rescues.filter(creation_date__gt=limit)\
            .extra({'date': "date_trunc('month', creation_date)"})
        self.rescue['by_month'] = by_month.values('date')\
                                          .annotate(number=Count('pk'))\
                                          .order_by('-date')

        self.rescue['by_dpt'] = FileByDepartment.objects\
            .filter(file__file_type=rescue_type, department__isnull=False)\
            .values('department__label')\
            .annotate(number=Count('file'))\
            .order_by('department__label')
        self.rescue['towns'] = FileTown.objects\
            .filter(file__file_type=rescue_type)\
            .values('town__name')\
            .annotate(number=Count('file'))\
            .order_by('-number', 'town__name')[:10]

        self.rescue['with_associated_operation'] = rescues\
            .filter(operations__isnull=False).count()

        if self.rescue['total_number']:
            self.rescue['with_associated_operation_percent'] = round(
                float(self.rescue['with_associated_operation'])
                / self.rescue['total_number'] * 100, 2)

        by_year_operationnal = rescues.filter(operations__isnull=False)\
            .extra({'date': 'date_trunc(\'year\', '
                            '"archaeological_files_file".creation_date)'})
        by_year_operationnal = by_year_operationnal.values('date')\
            .annotate(number=Count('pk')).order_by('-date')
        percents, idx = [], 0
        for dct in self.rescue['by_year']:
            if idx >= len(by_year_operationnal):
                break
            if by_year_operationnal[idx]['date'] != dct['date'] or\
               not dct['number']:
                continue
            val = round(float(by_year_operationnal[idx]['number']) /
                        dct['number'] * 100, 2)
            percents.append({'date': dct['date'], 'number': val})
        self.rescue['operational_by_year'] = percents

        self.rescue['surface_by_town'] = FileTown.objects\
            .filter(file__file_type=rescue_type)\
            .values('town__name')\
            .annotate(number=Sum('file__total_surface'))\
            .order_by('-number', 'town__name')[:10]
        self.rescue['surface_by_dpt'] = FileByDepartment.objects\
            .filter(file__file_type=rescue_type, department__isnull=False)\
            .values('department__label')\
            .annotate(number=Sum('file__total_surface'))\
            .order_by('department__label')
