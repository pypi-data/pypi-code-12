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

import datetime

from django.conf import settings
from django.contrib.gis.db import models
from django.core.urlresolvers import reverse
from django.db.models import Max, Q
from django.utils.translation import ugettext_lazy as _, ugettext

from ishtar_common.models import GeneralType, ImageModel, BaseHistorizedItem, \
    ShortMenuItem, LightHistorizedItem, HistoricalRecords, OwnPerms, Source, \
    Person, Basket

from archaeological_operations.models import AdministrativeAct
from archaeological_context_records.models import ContextRecord, Dating

from ishtar_common.models import PRIVATE_FIELDS
from archaeological_warehouse.models import Warehouse, Container


class MaterialType(GeneralType):
    code = models.CharField(_(u"Code"), max_length=10, blank=True, null=True)
    recommendation = models.TextField(_(u"Recommendation"), blank=True,
                                      null=True)
    parent = models.ForeignKey("MaterialType", blank=True, null=True,
                               verbose_name=_(u"Parent material"))

    class Meta:
        verbose_name = _(u"Material type")
        verbose_name_plural = _(u"Material types")
        ordering = ('label',)


class ConservatoryState(GeneralType):
    parent = models.ForeignKey("ConservatoryState", blank=True, null=True,
                               verbose_name=_(u"Parent conservatory state"))

    class Meta:
        verbose_name = _(u"Conservatory state")
        verbose_name_plural = _(u"Conservatory states")
        ordering = ('label',)


class PreservationType(GeneralType):
    class Meta:
        verbose_name = _(u"Preservation type")
        verbose_name_plural = _(u"Preservation types")
        ordering = ('label',)


class IntegrityType(GeneralType):
    class Meta:
        verbose_name = _(u"Integrity type")
        verbose_name_plural = _(u"Integrity type")
        ordering = ('label',)


class ObjectType(GeneralType):
    parent = models.ForeignKey("ObjectType", blank=True, null=True,
                               verbose_name=_(u"Parent"))

    class Meta:
        verbose_name = _(u"Object type")
        verbose_name_plural = _(u"Object types")
        ordering = ('parent__label', 'label',)

    def full_label(self):
        lbls = [self.label]
        item = self
        while item.parent:
            item = item.parent
            lbls.append(item.label)
        return u" > ".join(reversed(lbls))

    def __unicode__(self):
        return self.label

IS_ISOLATED_CHOICES = (
    ('U', _(u"Unknow")),
    ('O', _(u"Object")),
    ('B', _(u"Batch"))
)


class BaseFind(BaseHistorizedItem, OwnPerms):
    IS_ISOLATED_DICT = dict(IS_ISOLATED_CHOICES)
    label = models.TextField(_(u"Free ID"))
    external_id = models.CharField(_(u"External ID"), blank=True, null=True,
                                   max_length=120)
    description = models.TextField(_(u"Description"), blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    topographic_localisation = models.CharField(
        _(u"Topographic localisation"), blank=True, null=True, max_length=120)
    special_interest = models.CharField(_(u"Special interest"), blank=True,
                                        null=True, max_length=120)
    context_record = models.ForeignKey(
        ContextRecord, related_name='base_finds',
        verbose_name=_(u"Context Record"))
    discovery_date = models.DateField(_(u"Discovery date"),
                                      blank=True, null=True)
    batch = models.CharField(_(u"Batch/object"), max_length=1, default="U",
                             choices=IS_ISOLATED_CHOICES)
    index = models.IntegerField(u"Index", default=0)
    material_index = models.IntegerField(u"Material index", default=0)
    cache_short_id = models.TextField(
        _(u"Short ID"), blank=True, null=True,
        help_text=_(u"Cached value - do not edit"))
    cache_complete_id = models.TextField(
        _(u"Complete ID"), blank=True, null=True,
        help_text=_(u"Cached value - do not edit"))
    history = HistoricalRecords()
    RELATED_POST_PROCESS = ['find']

    class Meta:
        verbose_name = _(u"Base find")
        verbose_name_plural = _(u"Base finds")
        permissions = (
            ("view_basefind", ugettext(u"Can view all Base finds")),
            ("view_own_basefind", ugettext(u"Can view own Base find")),
            ("add_own_basefind", ugettext(u"Can add own Base find")),
            ("change_own_basefind", ugettext(u"Can change own Base find")),
            ("delete_own_basefind", ugettext(u"Can delete own Base find")),
        )

    def __unicode__(self):
        return self.label

    def get_last_find(self):
        # TODO: manage virtuals - property(last_find) ?
        finds = self.find.filter().order_by("-order").all()
        return finds and finds[0]

    @classmethod
    def get_max_index(cls, operation):
        q = BaseFind.objects\
            .filter(context_record__operation=operation)
        if q.count():
            return q.aggregate(Max('index'))['index__max']
        return 0

    def complete_id(self):
        # OPE|MAT.CODE|UE|FIND_index
        if not self.context_record.operation:
            return
        # find = self.get_last_find()
        ope = self.context_record.operation
        c_id = [unicode(ope.code_patriarche) if ope.code_patriarche else
                (unicode(ope.year) + "-" + unicode(ope.operation_code))]
        materials = set()
        for find in self.find.filter(downstream_treatment__isnull=True):
            for mat in find.material_types.all():
                if mat.code:
                    materials.add(mat.code)
        c_id.append(u'-'.join(sorted(list(materials))))
        c_id.append(self.context_record.label)
        max_index = str(self.get_max_index(ope))
        c_id.append((u'{:0' + str(len(max_index)) + 'd}').format(self.index))
        return settings.JOINT.join(c_id)

    def short_id(self):
        # OPE|FIND_index
        if not self.context_record.operation:
            return
        ope = self.context_record.operation
        c_id = [(ope.code_patriarche and unicode(ope.code_patriarche)) or
                (unicode(ope.year) + "-" + unicode(ope.operation_code))]
        max_index = str(self.get_max_index(ope))
        c_id.append((u'{:0' + str(len(max_index)) + 'd}').format(self.index))
        return settings.JOINT.join(c_id)

    def full_label(self):
        return self._real_label() or self._temp_label() or u""

    def material_type_label(self):
        find = self.get_last_find()
        finds = [find and find.material_type.code or '']
        ope = self.context_record.operation
        finds += [unicode(ope.code_patriarche) or
                  (unicode(ope.year) + "-" + unicode(ope.operation_code))]
        finds += [self.context_record.label, unicode(self.material_index)]
        return settings.JOINT.join(finds)

    def _real_label(self):
        if not self.context_record.parcel \
           or not self.context_record.operation \
           or not self.context_record.operation.code_patriarche:
            return
        find = self.get_last_find()
        lbl = find.label or self.label
        return settings.JOINT.join(
            [unicode(it) for it in (
                self.context_record.operation.code_patriarche,
                self.context_record.label, lbl) if it])

    def _temp_label(self):
        if not self.context_record.parcel:
            return
        find = self.get_last_find()
        lbl = find.label or self.label
        return settings.JOINT.join(
            [unicode(it) for it in (
                self.context_record.parcel.year, self.index,
                self.context_record.label, lbl) if it])

    @property
    def name(self):
        return self.label

    @classmethod
    def get_extra_fields(cls):
        fields = {}
        for field in Find._meta.many_to_many:
            if field.name == 'base_finds':
                fields['find'] = field.related.model
        return fields

WEIGHT_UNIT = (('g', _(u"g")),
               ('kg', _(u"kg")),)

CHECK_CHOICES = (('NC', _(u"Not checked")),
                 ('CI', _(u"Checked but incorrect")),
                 ('CC', _(u"Checked and correct")),
                 )


class FindBasket(Basket):
    items = models.ManyToManyField('Find', blank=True, null=True,
                                   related_name='basket')


class Find(BaseHistorizedItem, ImageModel, OwnPerms, ShortMenuItem):
    CHECK_DICT = dict(CHECK_CHOICES)
    SHOW_URL = 'show-find'
    TABLE_COLS = ['label', 'material_types', 'datings.period',
                  'base_finds.context_record.parcel.town',
                  'base_finds.context_record.operation.year',
                  'base_finds.context_record.operation.operation_code',
                  'container.reference', 'container.location',
                  'base_finds.batch']
    if settings.COUNTRY == 'fr':
        TABLE_COLS.insert(
            6, 'base_finds.context_record.operation.code_patriarche')
    TABLE_COLS_FOR_OPE = [
        'base_finds.cache_short_id',
        'base_finds.cache_complete_id',
        'previous_id', 'label', 'material_types',
        'datings.period', 'find_number', 'object_types',
        'description']

    EXTRA_FULL_FIELDS = [
        'base_finds.cache_short_id', 'base_finds.cache_complete_id',
        'base_finds.comment', 'base_finds.description',
        'base_finds.topographic_localisation',
        'base_finds.special_interest',
        'base_finds.discovery_date']
    EXTRA_FULL_FIELDS_LABELS = {
        'base_finds.cache_short_id': _(u"Base find - Short ID"),
        'base_finds.cache_complete_id': _(u"Base find - Complete ID"),
        'base_finds.comment': _(u"Base find - Comment"),
        'base_finds.description': _(u"Base find - Description"),
        'base_finds.topographic_localisation': _(u"Base find - "
                                                 u"Topographic localisation"),
        'base_finds.special_interest': _(u"Base find - Special interest"),
        'base_finds.discovery_date': _(u"Base find - Discovery date"),
    }
    ATTRS_EQUIV = {'get_first_base_find': 'base_finds'}
    base_finds = models.ManyToManyField(BaseFind, verbose_name=_(u"Base find"),
                                        related_name='find')
    external_id = models.CharField(_(u"External ID"), blank=True, null=True,
                                   max_length=120)
    order = models.IntegerField(_(u"Order"), default=1)
    label = models.TextField(_(u"Free ID"))
    description = models.TextField(_(u"Description"), blank=True, null=True)
    material_types = models.ManyToManyField(
        MaterialType, verbose_name=_(u"Material types"), related_name='finds')
    conservatory_state = models.ForeignKey(
        ConservatoryState, verbose_name=_(u"Conservatory state"), blank=True,
        null=True)
    preservation_to_considers = models.ManyToManyField(
        PreservationType, verbose_name=_(u"Type of preservation to consider"),
        related_name='finds')
    volume = models.FloatField(_(u"Volume (l)"), blank=True, null=True)
    weight = models.FloatField(_(u"Weight (g)"), blank=True, null=True)
    weight_unit = models.CharField(_(u"Weight unit"), max_length=4,
                                   blank=True, null=True, choices=WEIGHT_UNIT)
    find_number = models.IntegerField(_("Find number"), blank=True, null=True)
    upstream_treatment = models.ForeignKey(
        "Treatment", blank=True, null=True,
        related_name='downstream',
        verbose_name=_("Upstream treatment"))
    downstream_treatment = models.ForeignKey(
        "Treatment", blank=True, null=True, related_name='upstream',
        verbose_name=_("Downstream treatment"))
    datings = models.ManyToManyField(Dating, verbose_name=_(u"Dating"),
                                     related_name='find')
    container = models.ForeignKey(
        Container, verbose_name=_(u"Container"), blank=True, null=True,
        related_name='finds')
    is_complete = models.NullBooleanField(_(u"Is complete?"), blank=True,
                                          null=True)
    object_types = models.ManyToManyField(
        ObjectType, verbose_name=_(u"Object types"), related_name='find')
    integrities = models.ManyToManyField(
        IntegrityType, verbose_name=_(u"Integrity"), related_name='find')
    length = models.FloatField(_(u"Length (cm)"), blank=True, null=True)
    width = models.FloatField(_(u"Width (cm)"), blank=True, null=True)
    height = models.FloatField(_(u"Height (cm)"), blank=True, null=True)
    diameter = models.FloatField(_(u"Diameter (cm)"), blank=True, null=True)
    mark = models.TextField(_(u"Mark"), blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    dating_comment = models.TextField(_(u"Comment on dating"), blank=True,
                                      null=True)
    previous_id = models.TextField(_(u"Previous ID"), blank=True, null=True)
    index = models.IntegerField(u"Index", default=0)
    checked = models.CharField(_(u"Check"), max_length=2, default='NC',
                               choices=CHECK_CHOICES)
    check_date = models.DateField(_(u"Check date"),
                                  default=datetime.date.today)
    history = HistoricalRecords()
    BASKET_MODEL = FindBasket

    def __init__(self, *args, **kwargs):
        super(Find, self).__init__(*args, **kwargs)
        image = self._meta.get_field_by_name("image")[0]
        image.upload_to = "finds/"
        thumbnail = self._meta.get_field_by_name("thumbnail")[0]
        thumbnail.upload_to = "finds/thumbs/"

    class Meta:
        verbose_name = _(u"Find")
        verbose_name_plural = _(u"Finds")
        permissions = (
            ("view_find", ugettext(u"Can view all Finds")),
            ("view_own_find", ugettext(u"Can view own Find")),
            ("add_own_find", ugettext(u"Can add own Find")),
            ("change_own_find", ugettext(u"Can change own Find")),
            ("delete_own_find", ugettext(u"Can delete own Find")),
        )

    @property
    def short_class_name(self):
        return _(u"FIND")

    def __unicode__(self):
        return self.label

    @property
    def short_label(self):
        return self.reference

    @property
    def dating(self):
        return u" ; ".join([unicode(dating) for dating in self.datings.all()])

    @property
    def show_url(self):
        return reverse('show-find', args=[self.pk, ''])

    @property
    def name(self):
        return u" - ".join([base_find.name
                            for base_find in self.base_finds.all()])

    @property
    def full_label(self):
        lbl = u" - ".join([
            getattr(self, attr)
            for attr in ('label', 'administrative_index')
            if getattr(self, attr)])
        base = u" - ".join([base_find.complete_id()
                            for base_find in self.base_finds.all()])
        if base:
            lbl += u' ({})'.format(base)
        return lbl

    def get_first_base_find(self):
        q = self.base_finds
        if not q.count():
            return
        return q.order_by('-pk').all()[0]

    @property
    def reference(self):
        bf = self.get_first_base_find()
        if not bf:
            return "00"
        return bf.short_id()

    @property
    def administrative_index(self):
        bf = self.get_first_base_find()
        if not bf:
            return
        return "{}-{}".format(
            bf.context_record.operation.get_reference(),
            self.index)

    def upstream_treatments(self):
        treatments = []
        base_finds = [bf.pk for bf in self.base_finds.all()]
        if self.upstream_treatment and \
                self.upstream_treatment.pk not in treatments:
            treatments.append(
                (self.upstream_treatment.upstream.distinct(
                ).order_by('label').all(), self.upstream_treatment))
            for upstream in self.upstream_treatment.upstream.all():
                if upstream.pk != self.pk and not [
                        bf.pk for bf in upstream.base_finds.all()
                        if bf.pk in base_finds]:
                    continue
                for items, treatment in upstream.upstream_treatments():
                    if treatment.pk not in treatments:
                        treatments.append((treatment.upstream.order_by(
                            'label').all(), treatment))
        return treatments

    def downstream_treatments(self):
        treatments = []
        base_finds = [bf.pk for bf in self.base_finds.all()]
        if self.downstream_treatment and \
                self.downstream_treatment.pk not in treatments:
            treatments.append(
                (self.downstream_treatment.downstream.distinct(
                ).order_by('label').all(), self.downstream_treatment))
            for downstream in self.downstream_treatment.downstream.all():
                if downstream.pk != self.pk and not [
                        bf.pk for bf in downstream.base_finds.all()
                        if bf.pk in base_finds]:
                    continue
                for items, treatment in downstream.downstream_treatments():
                    if treatment.pk not in treatments:
                        treatments.append((treatment.downstream.order_by(
                            'label').all(), treatment))
        return treatments

    def get_department(self):
        bf = self.get_first_base_find()
        if not bf:
            return "00"
        return bf.context_record.operation.get_department()

    def get_town_label(self):
        bf = self.get_first_base_find()
        if not bf:
            return "00"
        return bf.context_record.operation.get_town_label()

    @classmethod
    def get_periods(cls, slice='year', fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        if slice == 'year':
            years = set()
            finds = q.filter(downstream_treatment__isnull=True)
            for find in finds:
                bi = find.base_finds.all()
                if not bi:
                    continue
                bi = bi[0]
                if bi.context_record.operation.start_date:
                    yr = bi.context_record.operation.start_date.year
                    years.add(yr)
        return list(years)

    @classmethod
    def get_by_year(cls, year, fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        return q.filter(
            downstream_treatment__isnull=True,
            base_finds__context_record__operation__start_date__year=year)

    @classmethod
    def get_operations(cls):
        operations = set()
        finds = cls.objects.filter(downstream_treatment__isnull=True)
        for find in finds:
            bi = find.base_finds.all()
            if not bi:
                continue
            bi = bi[0]
            pk = bi.context_record.operation.pk
            operations.add(pk)
        return list(operations)

    @classmethod
    def get_by_operation(cls, operation_id):
        return cls.objects.filter(
            downstream_treatment__isnull=True,
            base_finds__context_record__operation__pk=operation_id)

    @classmethod
    def get_total_number(cls, fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        return q.filter(downstream_treatment__isnull=True).count()

    def duplicate(self, user):
        model = self.__class__
        # base fields
        table_cols = [field.name for field in model._meta.fields
                      if field.name not in PRIVATE_FIELDS or
                      field.name == 'order']
        dct = dict([(attr, getattr(self, attr)) for attr in
                    table_cols])
        dct['order'] += 1
        dct['history_modifier'] = user
        new = self.__class__(**dct)
        new.save()

        # m2m fields
        m2m = [field.name for field in model._meta.many_to_many
               if field.name not in PRIVATE_FIELDS]
        for field in m2m:
            for val in getattr(self, field).all():
                getattr(new, field).add(val)
        return new

    @classmethod
    def get_query_owns(cls, user):
        return Q(base_finds__context_record__operation__scientist=user.
                 ishtaruser.person) |\
            Q(base_finds__context_record__operation__in_charge=user.
              ishtaruser.person) |\
            Q(history_creator=user)

    def save(self, *args, **kwargs):
        super(Find, self).save(*args, **kwargs)
        q = self.base_finds
        if not self.index and q.count():
            operation = q.filter(
                context_record__operation__pk__isnull=False).order_by(
                '-context_record__operation__start_date')
            if operation.count():
                operation = operation.all()[0].context_record.operation
                q = Find.objects\
                    .filter(base_finds__context_record__operation=operation)
                if self.pk:
                    q = q.exclude(pk=self.pk)
                if q.count():
                    self.index = q.aggregate(Max('index'))['index__max'] + 1
                else:
                    self.index = 1
                self.save()
        for base_find in self.base_finds.filter(
                context_record__operation__pk__isnull=False).all():
            modified = False
            if not base_find.index:
                modified = True
                base_find.index = BaseFind.get_max_index(
                    base_find.context_record.operation) + 1
            if not base_find.cache_short_id or \
                    not base_find.cache_short_id.endswith(
                        unicode(base_find.index)):
                base_find.cache_short_id = base_find.short_id()
                if base_find.cache_short_id:
                    modified = True
            if not base_find.cache_complete_id or \
                    not base_find.cache_complete_id.endswith(
                        unicode(base_find.index)):
                base_find.cache_complete_id = base_find.complete_id()
                if base_find.cache_complete_id:
                    modified = True
            if modified:
                base_find.save()
            # if not base_find.material_index:
            #    idx = BaseFind.objects\
            #                  .filter(context_record=base_find.context_record,
            #                          find__material_types=self.material_type)\
            #                  .aggregate(Max('material_index'))
            #    base_find.material_index = \
            #        idx and idx['material_index__max'] + 1 or 1


class FindSource(Source):
    SHOW_URL = 'show-findsource'

    class Meta:
        verbose_name = _(u"Find documentation")
        verbose_name_plural = _(u"Find documentations")
    find = models.ForeignKey(Find, verbose_name=_(u"Find"),
                             related_name="source")

    @property
    def owner(self):
        return self.find


class TreatmentType(GeneralType):
    virtual = models.BooleanField(_(u"Virtual"))

    class Meta:
        verbose_name = _(u"Treatment type")
        verbose_name_plural = _(u"Treatment types")
        ordering = ('label',)


class Treatment(BaseHistorizedItem, OwnPerms):
    external_id = models.CharField(_(u"External ID"), blank=True, null=True,
                                   max_length=120)
    container = models.ForeignKey(Container, verbose_name=_(u"Container"),
                                  blank=True, null=True)
    description = models.TextField(_(u"Description"), blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    treatment_type = models.ForeignKey(TreatmentType,
                                       verbose_name=_(u"Treatment type"))
    location = models.ForeignKey(Warehouse, verbose_name=_(u"Location"),
                                 blank=True, null=True)
    other_location = models.CharField(_(u"Other location"), max_length=200,
                                      blank=True, null=True)
    person = models.ForeignKey(
        Person, verbose_name=_(u"Person"), blank=True, null=True,
        on_delete=models.SET_NULL, related_name='treatments')
    start_date = models.DateField(_(u"Start date"), blank=True, null=True)
    end_date = models.DateField(_(u"End date"), blank=True, null=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = _(u"Treatment")
        verbose_name_plural = _(u"Treatments")
        permissions = (
            ("view_treatment", ugettext(u"Can view all Treatments")),
            ("view_own_treatment", ugettext(u"Can view own Treatment")),
            ("add_own_treatment", ugettext(u"Can add own Treatment")),
            ("change_own_treatment", ugettext(u"Can change own Treatment")),
            ("delete_own_treatment", ugettext(u"Can delete own Treatment")),
        )

    def __unicode__(self):
        lbl = unicode(self.treatment_type)
        if self.person:
            lbl += u" %s %s" % (_(u"by"), unicode(self.person))
        return lbl

    def save(self, *args, **kwargs):
        items, user, extra_args_for_new = [], None, []
        if "items" in kwargs:
            items = kwargs.pop('items')
        if "user" in kwargs:
            user = kwargs.pop('user')
        if "extra_args_for_new" in kwargs:
            extra_args_for_new = kwargs.pop('extra_args_for_new')
        is_new = self.pk is None
        super(Treatment, self).save(*args, **kwargs)
        if not is_new or not items:
            return
        basket = None
        if hasattr(items, "items"):
            basket = items
            items = basket.items.all()
        for item in items:
            new = item.duplicate(user)
            item.downstream_treatment = self
            item.save()
            new.upstream_treatment = self
            for k in extra_args_for_new:
                setattr(new, k, extra_args_for_new[k])
            new.save()
            # update baskets
            for basket in FindBasket.objects.filter(items__pk=item.pk).all():
                basket.items.remove(item)
                basket.items.add(new)


class TreatmentSource(Source):
    class Meta:
        verbose_name = _(u"Treatment documentation")
        verbose_name_plural = _(u"Treament documentations")
    treatment = models.ForeignKey(
        Treatment, verbose_name=_(u"Treatment"), related_name="source")

    @property
    def owner(self):
        return self.treatment


class Property(LightHistorizedItem):
    find = models.ForeignKey(Find, verbose_name=_(u"Find"))
    administrative_act = models.ForeignKey(
        AdministrativeAct, verbose_name=_(u"Administrative act"))
    person = models.ForeignKey(Person, verbose_name=_(u"Person"),
                               related_name='properties')
    start_date = models.DateField(_(u"Start date"))
    end_date = models.DateField(_(u"End date"))

    class Meta:
        verbose_name = _(u"Property")
        verbose_name_plural = _(u"Properties")

    def __unicode__(self):
        return self.person + settings.JOINT + self.find
