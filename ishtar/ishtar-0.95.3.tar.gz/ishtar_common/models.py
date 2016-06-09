#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Étienne Loks  <etienne.loks_AT_peacefrogsDOTnet>

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

"""
Models description
"""
from cStringIO import StringIO
import copy
import datetime
from PIL import Image
from importlib import import_module
import os
import re
import shutil
import tempfile
import unicodecsv
import zipfile

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.validators import validate_slug
from django.core.urlresolvers import reverse, NoReverseMatch
from django.db.utils import DatabaseError
from django.db.models import Q, Max, Count
from django.db.models.base import ModelBase
from django.db.models.signals import post_save, pre_delete, post_delete
from django.utils.translation import ugettext_lazy as _, ugettext, \
    pgettext_lazy

from django.utils.safestring import SafeUnicode, mark_safe
from django.template.defaultfilters import slugify

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.gis.db import models

from simple_history.models import HistoricalRecords as BaseHistoricalRecords

from ishtar_common.ooo_replace import ooo_replace
from ishtar_common.model_merging import merge_model_objects
from ishtar_common.utils import get_cache
from ishtar_common.data_importer import Importer, ImportFormater, \
    IntegerFormater, FloatFormater, UnicodeFormater, DateFormater, \
    TypeFormater, YearFormater, StrToBoolean, FileFormater


def post_save_user(sender, **kwargs):
    user = kwargs['instance']
    ishtaruser = None
    try:
        q = IshtarUser.objects.filter(username=user.username)
        if not q.count():
            ishtaruser = IshtarUser.create_from_user(user)
        else:
            ishtaruser = q.all()[0]
        ADMINISTRATOR, created = PersonType.objects.get_or_create(
            txt_idx='administrator')
        if ishtaruser.is_superuser \
           and not ishtaruser.has_right('administrator'):
            ishtaruser.person.person_types.add(ADMINISTRATOR)
    except DatabaseError:  # manage when db is not synced
        pass
post_save.connect(post_save_user, sender=User)


class Imported(models.Model):
    imports = models.ManyToManyField(
        'Import', blank=True, null=True,
        related_name="imported_%(app_label)s_%(class)s")

    class Meta:
        abstract = True


class ValueGetter(object):
    _prefix = ""
    GET_VALUES_EXTRA = []

    def get_values(self, prefix=''):
        if not prefix:
            prefix = self._prefix
        values = {}
        for field_name in self._meta.get_all_field_names():
            if not hasattr(self, field_name):
                continue
            value = getattr(self, field_name)
            if hasattr(value, 'get_values'):
                values.update(value.get_values(prefix + field_name + '_'))
            else:
                values[prefix + field_name] = value
        for extra_field in self.GET_VALUES_EXTRA:
            values[prefix + extra_field] = getattr(self, extra_field) or ''
        values['KEYS'] = u'\n'.join(values.keys())
        value_list = []
        for key in values.keys():
            if key in ('KEYS', 'VALUES'):
                continue
            value_list.append((key, unicode(values[key])))
        values['VALUES'] = u'\n'.join(
            [u"%s: %s" % (k, v) for k, v in sorted(value_list,
                                                   key=lambda x:x[0])])
        for global_var in GlobalVar.objects.all():
            values[global_var.slug] = global_var.value or ""
        return values

    @classmethod
    def get_empty_values(cls, prefix=''):
        if not prefix:
            prefix = cls._prefix
        values = {}
        for field_name in cls._meta.get_all_field_names():
            values[prefix + field_name] = ''
        return values


class HistoricalRecords(BaseHistoricalRecords):
    def create_historical_record(self, instance, type):
        try:
            history_modifier = getattr(instance, 'history_modifier', None)
            assert history_modifier
        except (User.DoesNotExist, AssertionError):
            # on batch removing of users, user could have disapeared
            return
        manager = getattr(instance, self.manager_name)
        attrs = {}
        for field in instance._meta.fields:
            attrs[field.attname] = getattr(instance, field.attname)
        q_history = instance.history\
            .filter(history_modifier_id=history_modifier.pk)\
            .order_by('-history_date', '-history_id')
        if not q_history.count():
            manager.create(history_type=type, **attrs)
            return
        old_instance = q_history.all()[0]
        # multiple saving by the same user in a very short time are generaly
        # caused by post_save signals it is not relevant to keep them
        min_history_date = datetime.datetime.now() \
            - datetime.timedelta(seconds=5)
        q = q_history.filter(history_date__isnull=False,
                             history_date__gt=min_history_date)\
                     .order_by('-history_date', '-history_id')
        if q.count():
            return

        # record a new version only if data have been changed
        for field in instance._meta.fields:
            if getattr(old_instance, field.attname) != attrs[field.attname]:
                manager.create(history_type=type, **attrs)
                return


def valid_id(cls):
    # valid ID validator for models
    def func(value):
        try:
            cls.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise ValidationError(_(u"Not a valid item."))
    return func


def valid_ids(cls):
    def func(value):
        if "," in value:
            value = value.split(",")
        for v in value:
            try:
                cls.objects.get(pk=v)
            except ObjectDoesNotExist:
                raise ValidationError(
                    _(u"A selected item is not a valid item."))
    return func


def is_unique(cls, field):
    # unique validator for models
    def func(value):
        query = {field: value}
        try:
            assert cls.objects.filter(**query).count() == 0
        except AssertionError:
            raise ValidationError(_(u"This item already exists."))
    return func


class OwnPerms:
    """
    Manage special permissions for object's owner
    """
    @classmethod
    def get_query_owns(cls, user):
        """
        Query object to get own items
        """
        return None  # implement for each object

    def is_own(self, user):
        """
        Check if the current object is owned by the user
        """
        query = self.get_query_owns(user)
        if not query:
            return False
        query = query & Q(pk=self.pk)
        return self.__class__.objects.filter(query).count()

    @classmethod
    def has_item_of(cls, user):
        """
        Check if the user own some items
        """
        query = cls.get_query_owns(user)
        if not query:
            return False
        return cls.objects.filter(query).count()

    @classmethod
    def get_owns(cls, user):
        """
        Get Own items
        """
        if isinstance(user, User):
            user = IshtarUser.objects.get(user_ptr=user)
        if user.is_anonymous():
            return cls.objects.filter(pk__isnull=True)
        items = []
        if hasattr(cls, 'BASKET_MODEL'):
            items = list(cls.BASKET_MODEL.objects.filter(user=user).all())
        query = cls.get_query_owns(user)
        if not query:
            return cls.objects.filter(pk__isnull=True)
        items += list(
            cls.objects.filter(query).order_by(*cls._meta.ordering).all())
        return items


class Cached(object):
    slug_field = 'txt_idx'

    @classmethod
    def get_cache(cls, slug):
        cache_key, value = get_cache(cls, slug)
        if value:
            return value
        try:
            k = {cls.slug_field: slug}
            obj = cls.objects.get(**k)
            cache.set(cache_key, obj, settings.CACHE_TIMEOUT)
            return obj
        except cls.DoesNotExist:
            return None


class GeneralType(models.Model, Cached):
    """
    Abstract class for "types"
    """
    label = models.CharField(_(u"Label"), max_length=100)
    txt_idx = models.CharField(
        _(u"Textual ID"), validators=[validate_slug], max_length=100,
        unique=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    available = models.BooleanField(_(u"Available"), default=True)
    HELP_TEXT = u""

    class Meta:
        abstract = True
        unique_together = (('txt_idx', 'available'),)

    def __unicode__(self):
        return self.label

    @classmethod
    def create_default_for_test(cls):
        return [cls.objects.create(label='Test %d' % i) for i in range(5)]

    @property
    def short_label(self):
        return self.label

    @classmethod
    def get_help(cls, dct={}, exclude=[]):
        help_text = cls.HELP_TEXT
        c_rank = -1
        help_items = u"\n"
        for item in cls.get_types(dct=dct, instances=True, exclude=exclude):
            if hasattr(item, '__iter__'):
                # TODO: manage multiple levels
                continue
            if not item.comment:
                continue
            if c_rank > item.rank:
                help_items += u"</dl>\n"
            elif c_rank < item.rank:
                help_items += u"<dl>\n"
            c_rank = item.rank
            help_items += u"<dt>%s</dt><dd>%s</dd>" % (
                item.label, u"<br/>".join(item.comment.split('\n')))
        c_rank += 1
        if c_rank:
            help_items += c_rank * u"</dl>"
        if help_text or help_items != u'\n':
            return mark_safe(help_text + help_items)
        return u""

    @classmethod
    def get_types(cls, dct={}, instances=False, exclude=[], empty_first=True,
                  default=None):
        base_dct = dct.copy()
        if hasattr(cls, 'parent'):
            return cls._get_parent_types(
                base_dct, instances, exclude=exclude, empty_first=empty_first,
                default=default)
        return cls._get_types(base_dct, instances, exclude=exclude,
                              empty_first=empty_first, default=default)

    @classmethod
    def _get_types(cls, dct={}, instances=False, exclude=[], empty_first=True,
                   default=None):
        dct['available'] = True
        if not instances and empty_first and not default:
            yield ('', '--')
        if default:
            try:
                default = cls.objects.get(txt_idx=default)
                yield(default.pk, _(unicode(default)))
            except cls.DoesNotExist:
                pass
        items = cls.objects.filter(**dct)
        if default:
            exclude.append(default.txt_idx)
        if exclude:
            items = items.exclude(txt_idx__in=exclude)
        for item in items.order_by(*cls._meta.ordering).all():
            if instances:
                item.rank = 0
                yield item
            else:
                yield (item.pk, _(unicode(item))
                       if item and unicode(item) else '')

    PREFIX = "&#x2502; "
    PREFIX_EMPTY = "&nbsp; "
    PREFIX_MEDIUM = "&#x251C; "
    PREFIX_LAST = "&#x2514; "

    @classmethod
    def _get_childs(cls, item, dct, prefix=0, instances=False, exclude=[],
                    is_last=False):
        prefix += 1
        dct['parent'] = item
        childs = cls.objects.filter(**dct)
        if exclude:
            childs = childs.exclude(txt_idx__in=exclude)
        if hasattr(cls, 'order'):
            childs = childs.order_by('order')
        lst = []
        child_lst = childs.all()
        total = len(child_lst)
        for idx, child in enumerate(child_lst):
            if instances:
                child.rank = prefix
                lst.append(child)
            else:
                p = ''
                cprefix = prefix
                while cprefix:
                    cprefix -= 1
                    if not cprefix:
                        if (idx + 1) == total:
                            p += cls.PREFIX_LAST
                        else:
                            p += cls.PREFIX_MEDIUM
                    elif is_last:
                        p += cls.PREFIX_EMPTY
                    else:
                        p += cls.PREFIX
                lst.append((
                    child.pk, SafeUnicode(p + unicode(_(unicode(child))))
                ))
            for sub_child in cls._get_childs(
                    child, dct, prefix, instances, exclude=exclude,
                    is_last=((idx + 1) == total)):
                lst.append(sub_child)
        return lst

    @classmethod
    def _get_parent_types(cls, dct={}, instances=False, exclude=[],
                          empty_first=True, default=None):
        dct['available'] = True
        if not instances and empty_first:
            yield ('', '--')
        dct['parent'] = None
        items = cls.objects.filter(**dct)
        if exclude:
            items = items.exclude(txt_idx__in=exclude)
        if hasattr(cls, 'order'):
            items = items.order_by('order')
        for item in items.all():
            if instances:
                item.rank = 0
                yield item
            else:
                yield (item.pk, unicode(item))
            for child in cls._get_childs(item, dct, instances,
                                         exclude=exclude):
                yield child

    def save(self, *args, **kwargs):
        if not self.id and not self.label:
            self.label = u" ".join(u" ".join(self.txt_idx.split('-'))
                                   .split('_')).title()
        if not self.txt_idx:
            self.txt_idx = slugify(self.label)[:100]

        # clean old keys
        if self.pk:
            old = self.__class__.objects.get(pk=self.pk)
            content_type = ContentType.objects.get_for_model(self.__class__)
            if slugify(self.label) != slugify(old.label):
                ItemKey.objects.filter(
                    object_id=self.pk, key=slugify(old.label),
                    content_type=content_type).delete()
            if self.txt_idx != old.txt_idx:
                ItemKey.objects.filter(
                    object_id=self.pk, key=old.txt_idx,
                    content_type=content_type).delete()

        obj = super(GeneralType, self).save(*args, **kwargs)
        self.generate_key(force=True)
        return obj

    def add_key(self, key, force=False):
        content_type = ContentType.objects.get_for_model(self.__class__)
        if not force and ItemKey.objects.filter(
                key=key, content_type=content_type).count():
            return
        if force:
            ItemKey.objects.filter(key=key, content_type=content_type)\
                           .exclude(object_id=self.pk).delete()
        ItemKey.objects.get_or_create(object_id=self.pk, key=key,
                                      content_type=content_type)

    def generate_key(self, force=False):
        for key in (slugify(self.label), self.txt_idx):
            self.add_key(key)

    def get_keys(self):
        keys = [self.txt_idx]
        content_type = ContentType.objects.get_for_model(self.__class__)
        for ik in ItemKey.objects.filter(content_type=content_type,
                                         object_id=self.pk).all():
            keys.append(ik.key)
        return keys

    @classmethod
    def generate_keys(cls):
        # content_type = ContentType.objects.get_for_model(cls)
        for item in cls.objects.all():
            item.generate_key()


class Basket(models.Model):
    """
    Abstract class for a basket
    Subclass must be defined with an "items" ManyToManyField
    """
    IS_BASKET = True
    label = models.CharField(_(u"Label"), max_length=1000)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    user = models.ForeignKey('IshtarUser', blank=True, null=True)
    available = models.BooleanField(_(u"Available"), default=True)

    class Meta:
        abstract = True
        unique_together = (('label', 'user'),)

    def __unicode__(self):
        return self.label

    def get_short_menu_class(self):
        return 'basket'

    @property
    def associated_filename(self):
        return "{}-{}".format(datetime.date.today().strftime(
            "%Y-%m-%d"), slugify(self.label))


class ItemKey(models.Model):
    key = models.CharField(_(u"Key"), max_length=100)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    importer = models.ForeignKey(
        'Import', null=True, blank=True,
        help_text=_(u"Specific key to an import"))

    def __unicode__(self):
        return self.key


class ImageModel(models.Model):
    image = models.ImageField(upload_to="upload/", blank=True, null=True)
    thumbnail = models.ImageField(upload_to='upload/thumbs/', blank=True,
                                  null=True)
    IMAGE_MAX_SIZE = settings.IMAGE_MAX_SIZE
    THUMB_MAX_SIZE = settings.THUMB_MAX_SIZE

    class Meta:
        abstract = True

    def has_changed(self, field):
        if not self.pk:
            return True
        manager = getattr(self.__class__, 'objects')
        old = getattr(manager.get(pk=self.pk), field)
        return not getattr(self, field) == old

    def create_thumb(self, image, size):
        """Returns the image resized to fit inside a box of the given size"""
        image.thumbnail(size, Image.ANTIALIAS)
        temp = StringIO()
        image.save(temp, 'jpeg')
        temp.seek(0)
        return SimpleUploadedFile('temp', temp.read())

    def save(self, *args, **kwargs):
        # manage images
        if self.has_changed('image') and self.image:
            # convert to jpg
            filename = os.path.splitext(os.path.split(self.image.name)[-1])[0]
            old_path = self.image.path
            filename = "%s.jpg" % filename
            try:
                image = Image.open(self.image.file)
                # convert to RGB
                if image.mode not in ('L', 'RGB'):
                    image = image.convert('RGB')

                # resize if necessary
                self.image.save(filename,
                                self.create_thumb(image, self.IMAGE_MAX_SIZE),
                                save=False)

                if old_path != self.image.path:
                    os.remove(old_path)

                # save the thumbnail
                self.thumbnail.save(
                    '_%s' % filename,
                    self.create_thumb(image, self.THUMB_MAX_SIZE),
                    save=False)
            except IOError:
                pass
        super(ImageModel, self).save(*args, **kwargs)


class HistoryError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

PRIVATE_FIELDS = ('id', 'history_modifier', 'order')


class BaseHistorizedItem(Imported):
    IS_BASKET = False
    history_modifier = models.ForeignKey(
        User, related_name='+', on_delete=models.SET_NULL,
        verbose_name=_(u"Last editor"), blank=True, null=True)
    history_creator = models.ForeignKey(
        User, related_name='+', on_delete=models.SET_NULL,
        verbose_name=_(u"Creator"), blank=True, null=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        assert hasattr(self, 'history_modifier')
        if not self.id:
            self.history_creator = self.history_modifier
        super(BaseHistorizedItem, self).save(*args, **kwargs)
        return True

    def get_previous(self, step=None, date=None, strict=True):
        """
        Get a "step" previous state of the item
        """
        assert step or date
        historized = self.history.all()
        item = None
        if step:
            assert len(historized) > step
            item = historized[step]
        else:
            for step, item in enumerate(historized):
                if item.history_date == date:
                    break
            # ended with no match
            if item.history_date != date:
                return
        item._step = step
        if len(historized) != (step + 1):
            item._previous = historized[step + 1].history_date
        else:
            item._previous = None
        if step > 0:
            item._next = historized[step - 1].history_date
        else:
            item._next = None
        item.history_date = historized[step].history_date
        model = self.__class__
        for k in model._meta.get_all_field_names():
            field = model._meta.get_field_by_name(k)[0]
            if hasattr(field, 'rel') and field.rel:
                if not hasattr(item, k + '_id'):
                    setattr(item, k, getattr(self, k))
                    continue
                val = getattr(item, k + '_id')
                if not val:
                    setattr(item, k, None)
                    continue
                try:
                    val = field.rel.to.objects.get(pk=val)
                    setattr(item, k, val)
                except ObjectDoesNotExist:
                    if strict:
                        raise HistoryError(u"The class %s has no pk %d" % (
                                           unicode(field.rel.to), val))
                    setattr(item, k, None)
        item.pk = self.pk
        return item

    @property
    def last_edition_date(self):
        try:
            return self.history.order_by('-history_date').all()[0].history_date
        except IndexError:
            return

    def rollback(self, date):
        """
        Rollback to a previous state
        """
        to_del, new_item = [], None
        for item in self.history.all():
            if item.history_date == date:
                new_item = item
                break
            to_del.append(item)
        if not new_item:
            raise HistoryError(u"The date to rollback to doesn't exist.")
        try:
            for f in self._meta.fields:
                k = f.name
                if k != 'id' and hasattr(self, k):
                    if not hasattr(new_item, k):
                        k = k + "_id"
                    setattr(self, k, getattr(new_item, k))
            try:
                self.history_modifier = User.objects.get(
                    pk=new_item.history_modifier_id)
            except User.ObjectDoesNotExist:
                pass
            self.save()
        except:
            raise HistoryError(u"The rollback has failed.")
        # clean the obsolete history
        for historized_item in to_del:
            historized_item.delete()

    def values(self):
        values = {}
        for f in self._meta.fields:
            k = f.name
            if k != 'id':
                values[k] = getattr(self, k)
        return values

    def get_show_url(self):
        try:
            return reverse('show-' + self.__class__.__name__.lower(),
                           args=[self.pk, ''])
        except NoReverseMatch:
            return

    @property
    def associated_filename(self):
        if [True for attr in ('get_town_label', 'get_department', 'reference',
                              'short_class_name') if not hasattr(self, attr)]:
            return ''
        items = [slugify(self.get_department()),
                 slugify(self.get_town_label()).upper(),
                 slugify(self.short_class_name),
                 slugify(self.reference),
                 slugify(self.name or '').replace('-', '_').capitalize()]
        last_edition_date = self.last_edition_date
        if last_edition_date:
            items.append(last_edition_date.strftime('%Y%m%d'))
        else:
            items.append('00000000')
        return u"-".join([unicode(item) for item in items])


class GeneralRelationType(GeneralType):
    order = models.IntegerField(_(u"Order"), default=1)
    symmetrical = models.BooleanField(_(u"Symmetrical"))
    # # an inverse must be set
    # inverse_relation = models.ForeignKey(
    #    'RelationType', verbose_name=_(u"Inverse relation"), blank=True,
    #    null=True)

    class Meta:
        abstract = True

    def clean(self):
        # cannot have symmetrical and an inverse_relation
        if self.symmetrical and self.inverse_relation:
            raise ValidationError(
                _(u"Cannot have symmetrical and an inverse_relation"))

    def save(self, *args, **kwargs):
        obj = super(GeneralRelationType, self).save(*args, **kwargs)
        # after saving check that the inverse_relation of the inverse_relation
        # point to the saved object
        if self.inverse_relation \
           and (not self.inverse_relation.inverse_relation
                or self.inverse_relation.inverse_relation != self):
            self.inverse_relation.inverse_relation = self
            self.inverse_relation.symmetrical = False
            self.inverse_relation.save()
        return obj


class GeneralRecordRelations(object):
    def save(self, *args, **kwargs):
        super(GeneralRecordRelations, self).save(*args, **kwargs)

        # after saving create the symetric or the inverse relation

        sym_rel_type = self.relation_type
        if not self.relation_type.symmetrical:
            sym_rel_type = self.relation_type.inverse_relation

        # no symetric/inverse is defined
        if not sym_rel_type:
            return

        dct = {'right_record': self.left_record,
               'left_record': self.right_record, 'relation_type': sym_rel_type}
        self.__class__.objects.get_or_create(**dct)
        return self


def post_delete_record_relation(sender, instance, **kwargs):
    # delete symmetrical or inverse relation
    sym_rel_type = instance.relation_type
    if not instance.relation_type.symmetrical:
        sym_rel_type = instance.relation_type.inverse_relation

    # no symetric/inverse is defined
    if not sym_rel_type:
        return

    dct = {'right_record': instance.left_record,
           'left_record': instance.right_record,
           'relation_type': sym_rel_type}
    instance.__class__.objects.filter(**dct).delete()


class ShortMenuItem(object):
    def get_short_menu_class(self):
        return ''


class LightHistorizedItem(BaseHistorizedItem):
    history_date = models.DateTimeField(default=datetime.datetime.now)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        super(LightHistorizedItem, self).save(*args, **kwargs)
        return True


class IshtarSiteProfile(models.Model, Cached):
    slug_field = 'slug'
    label = models.TextField(_(u"Name"))
    slug = models.SlugField(_(u"Slug"), unique=True)
    description = models.TextField(_(u"Description"), null=True, blank=True)
    files = models.BooleanField(_(u"Files module"), default=False)
    context_record = models.BooleanField(_(u"Context records module"),
                                         default=False)
    find = models.BooleanField(_(u"Finds module"), default=False,
                               help_text=_(u"Need context records module"))
    warehouse = models.BooleanField(
        _(u"Warehouses module"), default=False,
        help_text=_(u"Need finds module"))
    homepage = models.TextField(
        _(u"Home page"), null=True, blank=True,
        help_text=_(u"Homepage of Ishtar - if not defined a default homepage "
                    u"will appear. Use the markdown syntax."))
    active = models.BooleanField(_(u"Current active"), default=False)

    class Meta:
        verbose_name = _(u"Ishtar site profile")
        verbose_name_plural = _(u"Ishtar site profiles")
        ordering = ['label']

    def __unicode__(self):
        return unicode(self.label)

    def save(self, *args, **kwargs):
        raw = False
        if 'raw' in kwargs:
            raw = kwargs.pop('raw')
        super(IshtarSiteProfile, self).save(*args, **kwargs)
        obj = self
        if raw:
            return obj
        q = self.__class__.objects.filter(active=True).exclude(slug=self.slug)
        if obj.active and q.count():
            for profile in q.all():
                profile.active = False
                profile.save(raw=True)
        changed = False
        if not obj.active and not q.count():
            obj.active = True
            changed = True
        if obj.warehouse and not obj.find:
            obj.find = True
            changed = True
        if obj.find and not obj.context_record:
            obj.context_record = True
            changed = True
        if changed:
            obj = obj.save(raw=True)
        return obj


def get_current_profile(force=False):
    cache_key, value = get_cache(IshtarSiteProfile, ['is-current-profile'])
    if value and not force:
        return value
    q = IshtarSiteProfile.objects.filter(active=True)
    if not q.count():
        obj = IshtarSiteProfile.objects.create(
            label="Default profile", slug='default', active=True)
    else:
        obj = q.all()[0]
    cache.set(cache_key, obj, settings.CACHE_TIMEOUT)
    return obj


def cached_site_changed(sender, **kwargs):
    get_current_profile(force=True)

post_save.connect(cached_site_changed, sender=IshtarSiteProfile)
post_delete.connect(cached_site_changed, sender=IshtarSiteProfile)


class GlobalVar(models.Model, Cached):
    slug = models.SlugField(_(u"Variable name"), unique=True)
    description = models.TextField(_(u"Description of the variable"),
                                   null=True, blank=True)
    value = models.TextField(_(u"Value"), null=True, blank=True)

    class Meta:
        verbose_name = _(u"Global variable")
        verbose_name_plural = _(u"Global variables")
        ordering = ['slug']

    def __unicode__(self):
        return unicode(self.slug)


def cached_globalvar_changed(sender, **kwargs):
    if not kwargs['instance']:
        return
    var = kwargs['instance']
    cache_key, value = get_cache(GlobalVar, var.slug)
    cache.set(cache_key, var.value, settings.CACHE_TIMEOUT)

post_save.connect(cached_globalvar_changed, sender=GlobalVar)


class UserDashboard:
    def __init__(self):
        types = IshtarUser.objects.values('person__person_types',
                                          'person__person_types__label')
        self.types = types.annotate(number=Count('pk'))\
                          .order_by('person__person_types')


class DashboardFormItem(object):
    @classmethod
    def get_periods(cls, slice='month', fltr={}, date_source='creation'):
        date_var = date_source + '_date'
        q = cls.objects.filter(**{date_var + '__isnull': False})
        if fltr:
            q = q.filter(**fltr)
        if slice == 'year':
            return [res[date_var].year for res in list(q.values(date_var)
                    .annotate(Count("id")).order_by())]
        elif slice == 'month':
            return [(res[date_var].year, res[date_var].month)
                    for res in list(q.values(date_var)
                    .annotate(Count("id")).order_by())]
        return []

    @classmethod
    def get_by_year(cls, year, fltr={}, date_source='creation'):
        date_var = date_source + '_date'
        q = cls.objects.filter(**{date_var + '__isnull': False})
        if fltr:
            q = q.filter(**fltr)
        return q.filter(**{date_var + '__year': year}).distinct('pk')

    @classmethod
    def get_by_month(cls, year, month, fltr={}, date_source='creation'):
        date_var = date_source + '_date'
        q = cls.objects.filter(**{date_var + '__isnull': False})
        if fltr:
            q = q.filter(**fltr)
        q = q.filter(
            **{date_var + '__year': year, date_var + '__month': month})
        return q.distinct('pk')

    @classmethod
    def get_total_number(cls, fltr={}):
        q = cls.objects
        if fltr:
            q = q.filter(**fltr)
        return q.distinct('pk').count()


class Dashboard:
    def __init__(self, model, slice='year', date_source=None, show_detail=None,
                 fltr={}):
        # don't provide date_source if it is not relevant
        self.model = model
        self.total_number = model.get_total_number(fltr)
        self.show_detail = show_detail
        history_model = self.model.history.model
        # last edited - created
        self.recents, self.lasts = [], []
        for last_lst, modif_type in ((self.lasts, '+'), (self.recents, '~')):
            last_ids = history_model.objects.values('id')\
                                            .annotate(hd=Max('history_date'))
            last_ids = last_ids.filter(history_type=modif_type)
            from archaeological_finds.models import Find
            if self.model == Find:
                last_ids = last_ids.filter(
                    downstream_treatment_id__isnull=True)
                if modif_type == '+':
                    last_ids = last_ids.filter(
                        upstream_treatment_id__isnull=True)
            last_ids = last_ids.order_by('-hd').distinct().all()[:5]
            for idx in last_ids:
                try:
                    obj = self.model.objects.get(pk=idx['id'])
                except:
                    # deleted object are always referenced in history
                    continue
                obj.history_date = idx['hd']
                last_lst.append(obj)
        # years
        base_kwargs = {'fltr': fltr.copy()}
        if date_source:
            base_kwargs['date_source'] = date_source
        periods_kwargs = copy.deepcopy(base_kwargs)
        periods_kwargs['slice'] = slice
        self.periods = model.get_periods(**periods_kwargs)
        self.periods = list(set(self.periods))
        self.periods.sort()
        if not self.total_number or not self.periods:
            return
        kwargs_num = copy.deepcopy(base_kwargs)
        self.serie_labels = [_(u"Total")]
        # numbers
        if slice == 'year':
            self.values = [('year', "",
                           list(reversed(self.periods)))]
            self.numbers = [model.get_by_year(year, **kwargs_num).count()
                            for year in self.periods]
            self.values += [('number', _(u"Number"),
                            list(reversed(self.numbers)))]
        if slice == 'month':
            periods = list(reversed(self.periods))
            self.periods = ["%d-%s-01" % (p[0], ('0' + str(p[1]))
                            if len(str(p[1])) == 1 else p[1]) for p in periods]
            self.values = [('month', "", self.periods)]
            if show_detail:
                for dpt in settings.ISHTAR_DPTS:
                    self.serie_labels.append(unicode(dpt))
                    idx = 'number_' + unicode(dpt)
                    kwargs_num['fltr']["towns__numero_insee__startswith"] = \
                        unicode(dpt)
                    numbers = [model.get_by_month(*p.split('-')[:2],
                                                  **kwargs_num).count()
                               for p in self.periods]
                    self.values += [(idx, dpt, list(numbers))]
                # put "Total" at the end
                self.serie_labels.append(self.serie_labels.pop(0))
            kwargs_num = base_kwargs.copy()
            self.numbers = [model.get_by_month(*p.split('-')[:2],
                                               **kwargs_num).count()
                            for p in self.periods]
            self.values += [('number', _(u"Total"),
                            list(self.numbers))]
        # calculate
        self.average = self.get_average()
        self.variance = self.get_variance()
        self.standard_deviation = self.get_standard_deviation()
        self.median = self.get_median()
        self.mode = self.get_mode()
        # by operation
        if not hasattr(model, 'get_by_operation'):
            return
        operations = model.get_operations()
        operation_numbers = [model.get_by_operation(op).count()
                             for op in operations]
        # calculate
        self.operation_average = self.get_average(operation_numbers)
        self.operation_variance = self.get_variance(operation_numbers)
        self.operation_standard_deviation = self.get_standard_deviation(
            operation_numbers)
        self.operation_median = self.get_median(operation_numbers)
        operation_mode_pk = self.get_mode(dict(zip(operations,
                                                   operation_numbers)))
        if operation_mode_pk:
            from archaeological_operations.models import Operation
            self.operation_mode = unicode(Operation.objects
                                                   .get(pk=operation_mode_pk))

    def get_average(self, vals=[]):
        if not vals:
            vals = self.numbers[:]
        return sum(vals) / len(vals)

    def get_variance(self, vals=[]):
        if not vals:
            vals = self.numbers[:]
        avrg = self.get_average(vals)
        return self.get_average([(x - avrg) ** 2 for x in vals])

    def get_standard_deviation(self, vals=[]):
        if not vals:
            vals = self.numbers[:]
        return round(self.get_variance(vals) ** 0.5, 3)

    def get_median(self, vals=[]):
        if not vals:
            vals = self.numbers[:]
        len_vals = len(vals)
        vals.sort()
        if (len_vals % 2) == 1:
            return vals[len_vals / 2]
        else:
            return (vals[len_vals / 2 - 1] + vals[len_vals / 2]) / 2.0

    def get_mode(self, vals={}):
        if not vals:
            vals = dict(zip(self.periods, self.numbers[:]))
        mx = max(vals.values())
        for v in vals:
            if vals[v] == mx:
                return v


class DocumentTemplate(models.Model):
    CLASSNAMES = (('archaeological_operations.models.AdministrativeAct',
                  _(u"Administrative Act")),)
    name = models.CharField(_(u"Name"), max_length=100)
    template = models.FileField(_(u"Template"), upload_to="upload/templates/")
    associated_object_name = models.CharField(
        _(u"Associated object"), max_length=100, choices=CLASSNAMES)
    available = models.BooleanField(_(u"Available"), default=True)

    class Meta:
        verbose_name = _(u"Document template")
        verbose_name_plural = _(u"Document templates")
        ordering = ['associated_object_name', 'name']

    def __unicode__(self):
        return self.name

    @classmethod
    def get_tuples(cls, dct={}, empty_first=True):
        dct['available'] = True
        if empty_first:
            yield ('', '----------')
        items = cls.objects.filter(**dct)
        for item in items.distinct().order_by(*cls._meta.ordering).all():
            yield (item.pk, _(unicode(item)))

    def publish(self, c_object):
        tempdir = tempfile.mkdtemp("-ishtardocs")
        output_name = tempdir + os.path.sep + \
            slugify(self.name.replace(' ', '_').lower()) + u'-' +\
            datetime.date.today().strftime('%Y-%m-%d') +\
            u"." + self.template.name.split('.')[-1]
        values = c_object.get_values()
        ooo_replace(self.template, output_name, values)
        return output_name


class State(models.Model):
    label = models.CharField(_(u"Label"), max_length=30)
    number = models.CharField(_(u"Number"), unique=True, max_length=3)

    class Meta:
        verbose_name = _(u"State")
        ordering = ['number']

    def __unicode__(self):
        return self.label


class Department(models.Model):
    label = models.CharField(_(u"Label"), max_length=30)
    number = models.CharField(_(u"Number"), unique=True, max_length=3)
    state = models.ForeignKey('State', verbose_name=_(u"State"), blank=True,
                              null=True)

    class Meta:
        verbose_name = _(u"Department")
        verbose_name_plural = _(u"Departments")
        ordering = ['number']

    def __unicode__(self):
        return self.label


class Address(BaseHistorizedItem):
    address = models.TextField(_(u"Address"), null=True, blank=True)
    address_complement = models.TextField(_(u"Address complement"), null=True,
                                          blank=True)
    postal_code = models.CharField(_(u"Postal code"), max_length=10, null=True,
                                   blank=True)
    town = models.CharField(_(u"Town"), max_length=70, null=True, blank=True)
    country = models.CharField(_(u"Country"), max_length=30, null=True,
                               blank=True)
    alt_address = models.TextField(_(u"Other address: address"), null=True,
                                   blank=True)
    alt_address_complement = models.TextField(
        _(u"Other address: address complement"), null=True, blank=True)
    alt_postal_code = models.CharField(_(u"Other address: postal code"),
                                       max_length=10, null=True, blank=True)
    alt_town = models.CharField(_(u"Other address: town"), max_length=70,
                                null=True, blank=True)
    alt_country = models.CharField(_(u"Other address: country"),
                                   max_length=30, null=True, blank=True)
    phone = models.CharField(_(u"Phone"), max_length=18, null=True, blank=True)
    phone_desc = models.CharField(_(u"Phone description"), max_length=300,
                                  null=True, blank=True)
    phone2 = models.CharField(_(u"Phone description 2"), max_length=18,
                              null=True, blank=True)
    phone_desc2 = models.CharField(_(u"Phone description 2"), max_length=300,
                                   null=True, blank=True)
    phone3 = models.CharField(_(u"Phone 3"), max_length=18, null=True,
                              blank=True)
    phone_desc3 = models.CharField(_(u"Phone description 3"), max_length=300,
                                   null=True, blank=True)
    raw_phone = models.TextField(_(u"Raw phone"), blank=True, null=True)
    mobile_phone = models.CharField(_(u"Mobile phone"), max_length=18,
                                    null=True, blank=True)
    email = models.EmailField(
        _(u"Email"), max_length=300, blank=True, null=True)
    alt_address_is_prefered = models.BooleanField(
        _(u"Alternative address is prefered"), default=False)
    history = HistoricalRecords()

    class Meta:
        abstract = True

    def simple_lbl(self):
        return unicode(self)

    def full_address(self):
        lbl = self.simple_lbl()
        if lbl:
            lbl += u"\n"
        lbl += self.address_lbl()
        return lbl

    def address_lbl(self):
        lbl = u''
        prefix = ''
        if self.alt_address_is_prefered:
            prefix = 'alt_'
        if getattr(self, prefix + 'address'):
            lbl += getattr(self, prefix + 'address')
        if getattr(self, prefix + 'address_complement'):
            if lbl:
                lbl += "\n"
            lbl += getattr(self, prefix + 'address_complement')
        postal_code = getattr(self, prefix + 'postal_code')
        town = getattr(self, prefix + 'town')
        if postal_code or town:
            if lbl:
                lbl += "\n"
            lbl += u"{}{}{}".format(
                postal_code or '',
                " " if postal_code and town else '',
                town or '')
        if self.phone:
            if lbl:
                lbl += u"\n"
            lbl += u"{}{}".format(unicode(_("Tel: ")), self.phone)
        if self.mobile_phone:
            if lbl:
                lbl += u"\n"
            lbl += u"{}{}".format(unicode(_("Mobile: ")), self.mobile_phone)
        if self.email:
            if lbl:
                lbl += u"\n"
            lbl += u"{}{}".format(unicode(_("Email: ")), self.email)
        return lbl


class Merge(models.Model):
    merge_key = models.TextField(_("Merge key"), blank=True, null=True)
    merge_candidate = models.ManyToManyField("self",
                                             blank=True, null=True)
    merge_exclusion = models.ManyToManyField("self",
                                             blank=True, null=True)
    exclude_from_merge = models.NullBooleanField(default=False,
                                                 blank=True, null=True)
    # 1 for one word similarity, 2 for two word similarity, etc.
    MERGE_CLEMENCY = None
    EMPTY_MERGE_KEY = '--'

    class Meta:
        abstract = True

    def generate_merge_key(self):
        if self.exclude_from_merge:
            return
        self.merge_key = slugify(self.name if self.name else '')
        if not self.merge_key:
            self.merge_key = self.EMPTY_MERGE_KEY
        self.merge_key = self.merge_key

    def generate_merge_candidate(self):
        if self.exclude_from_merge:
            return
        if not self.merge_key:
            self.generate_merge_key()
            self.save()
        if not self.pk or self.merge_key == self.EMPTY_MERGE_KEY:
            return
        q = self.__class__.objects\
                          .exclude(pk=self.pk)\
                          .exclude(merge_exclusion=self)\
                          .exclude(merge_candidate=self)\
                          .exclude(exclude_from_merge=True)
        if not self.MERGE_CLEMENCY:
            q = q.filter(merge_key=self.merge_key)
        else:
            subkeys_front = u"-".join(
                self.merge_key.split('-')[:self.MERGE_CLEMENCY])
            subkeys_back = u"-".join(
                self.merge_key.split('-')[-self.MERGE_CLEMENCY:])
            q = q.filter(Q(merge_key__istartswith=subkeys_front) |
                         Q(merge_key__iendswith=subkeys_back))
        for item in q.all():
            self.merge_candidate.add(item)

    def save(self, *args, **kwargs):
        self.generate_merge_key()
        item = super(Merge, self).save(*args, **kwargs)
        self.generate_merge_candidate()
        return item

    def merge(self, item):
        merge_model_objects(self, item)
        self.generate_merge_candidate()


class OrganizationType(GeneralType):
    class Meta:
        verbose_name = _(u"Organization type")
        verbose_name_plural = _(u"Organization types")
        ordering = ('label',)

IMPORTER_CLASSES = {}

IMPORTER_CLASSES.update({
    'sra-pdl-files':
    'archaeological_files.data_importer.FileImporterSraPdL'})


def get_importer_models():
    MODELS = [
        ('ishtar_common.models.Person', _(u"Person")),
        ('ishtar_common.models.Organization', _(u"Organization")),
        ('archaeological_operations.models.Operation', _(u"Operation")),
        ('archaeological_operations.models.ArchaeologicalSite',
         _(u"Archaeological site")),
        ('archaeological_operations.models.Parcel', _(u"Parcels")),
        ('archaeological_operations.models.OperationSource',
         _(u"Operation source")),
    ]
    MODELS = [('archaeological_files.models.File',
              _(u"Archaeological files"))] + MODELS
    MODELS = [('archaeological_context_records.models.ContextRecord',
              _(u"Context records")),
              ('archaeological_context_records.models.RecordRelations',
              _(u"Context record relations"))] + MODELS
    MODELS = [('archaeological_finds.models.BaseFind',
              _(u"Finds")), ] + MODELS
    return MODELS


def get_model_fields(model):
    """
    Return a dict of fields from  model
    To be replace in Django 1.8 with get_fields, get_field
    """
    fields = {}
    options = model._meta
    for field in sorted(options.fields + options.many_to_many):
        fields[field.name] = field
    if hasattr(model, 'get_extra_fields'):
        fields.update(model.get_extra_fields())
    return fields


def import_class(full_path_classname):
    mods = full_path_classname.split('.')
    if len(mods) == 1:
        mods = ['ishtar_common', 'models', mods[0]]
    module = import_module('.'.join(mods[:-1]))
    return getattr(module, mods[-1])


class ImporterType(models.Model):
    """
    Description of a table to be mapped with ishtar database
    """
    name = models.CharField(_(u"Name"), blank=True, null=True,
                            max_length=100)
    slug = models.SlugField(_(u"Slug"), unique=True, blank=True, null=True,
                            max_length=100)
    description = models.CharField(_(u"Description"), blank=True, null=True,
                                   max_length=500)
    users = models.ManyToManyField('IshtarUser', verbose_name=_(u"Users"),
                                   blank=True, null=True)
    associated_models = models.CharField(_(u"Associated model"),
                                         max_length=200,
                                         choices=get_importer_models())
    is_template = models.BooleanField(_(u"Is template"), default=False)
    unicity_keys = models.CharField(_(u"Unicity keys (separator \";\")"),
                                    blank=True, null=True, max_length=500)

    class Meta:
        verbose_name = _(u"Importer - Type")
        verbose_name_plural = _(u"Importer - Types")

    def __unicode__(self):
        return self.name

    def get_importer_class(self):
        if self.slug and self.slug in IMPORTER_CLASSES:
            cls = import_class(IMPORTER_CLASSES[self.slug])
            return cls
        OBJECT_CLS = import_class(self.associated_models)
        DEFAULTS = dict([(default.keys, default.values)
                         for default in self.defaults.all()])
        LINE_FORMAT = []
        idx = 0
        for column in self.columns.order_by('col_number').all():
            idx += 1
            while column.col_number > idx:
                LINE_FORMAT.append(None)
                idx += 1
            targets = []
            formater_types = []
            nb = column.targets.count()
            if not nb:
                LINE_FORMAT.append(None)
                continue
            force_news = []
            concat_str = []
            for target in column.targets.all():
                ft = target.formater_type.get_formater_type(target)
                if not ft:
                    continue
                formater_types.append(ft)
                targets.append(target.target)
                concat_str.append(target.concat_str)
                force_news.append(target.force_new)
            formater_kwargs = {}
            if column.regexp_pre_filter:
                formater_kwargs['regexp'] = re.compile(
                    column.regexp_pre_filter.regexp)
            formater_kwargs['concat_str'] = concat_str
            formater_kwargs['duplicate_fields'] = [
                (field.field_name, field.force_new, field.concat,
                 field.concat_str)
                for field in column.duplicate_fields.all()]
            formater_kwargs['required'] = column.required
            formater_kwargs['force_new'] = force_news
            formater = ImportFormater(targets, formater_types,
                                      **formater_kwargs)
            LINE_FORMAT.append(formater)
        UNICITY_KEYS = []
        if self.unicity_keys:
            UNICITY_KEYS = [un.strip() for un in self.unicity_keys.split(';')]
        args = {'OBJECT_CLS': OBJECT_CLS, 'DESC': self.description,
                'DEFAULTS': DEFAULTS, 'LINE_FORMAT': LINE_FORMAT,
                'UNICITY_KEYS': UNICITY_KEYS}
        name = str(''.join(
            x for x in slugify(self.name).replace('-', ' ').title()
            if not x.isspace()))
        newclass = type(name, (Importer,), args)
        return newclass


def get_associated_model(parent_model, keys):
    model = None
    OBJECT_CLS = None
    if isinstance(parent_model, unicode) or \
       isinstance(parent_model, str):
        OBJECT_CLS = import_class(parent_model)
    else:
        OBJECT_CLS = parent_model
    for idx, item in enumerate(keys):
        if not idx:
            field = get_model_fields(OBJECT_CLS)[item]
            if hasattr(field, 'rel') and hasattr(field.rel, 'to'):
                model = field.rel.to
            if type(field) == ModelBase:
                model = field
        else:
            return get_associated_model(model, keys[1:])
    return model


class ImporterDefault(models.Model):
    """
    Targets of default values in an import
    """
    importer_type = models.ForeignKey(ImporterType, related_name='defaults')
    target = models.CharField(u"Target", max_length=500)

    class Meta:
        verbose_name = _(u"Importer - Default")
        verbose_name_plural = _(u"Importer - Defaults")

    def __unicode__(self):
        return u"{} - {}".format(self.importer_type, self.target)

    @property
    def keys(self):
        return tuple(self.target.split('__'))

    @property
    def associated_model(self):
        return get_associated_model(self.importer_type.associated_models,
                                    self.keys)

    @property
    def values(self):
        values = {}
        for default_value in self.default_values.all():
            values[default_value.target] = default_value.get_value()
        return values


class ImporterDefaultValues(models.Model):
    """
    Default values in an import
    """
    default_target = models.ForeignKey(ImporterDefault,
                                       related_name='default_values')
    target = models.CharField(u"Target", max_length=500)
    value = models.CharField(u"Value", max_length=500)

    def __unicode__(self):
        return u"{} - {}".format(self.default_target, self.target, self.value)

    class Meta:
        verbose_name = _(u"Importer - Default value")
        verbose_name_plural = _(u"Importer - Default values")

    def get_value(self):
        parent_model = self.default_target.associated_model
        if not parent_model:
            return self.value
        fields = get_model_fields(parent_model)
        target = self.target.strip()
        if target not in fields:
            return
        field = fields[target]
        if not hasattr(field, 'rel') or not hasattr(field.rel, 'to'):
            return
        model = field.rel.to
        # if value is an id
        try:
            return model.objects.get(pk=int(self.value))
        except (ValueError, model.DoesNotExist):
            pass
        # try with txt_idx
        try:
            return model.objects.get(txt_idx=self.value)
        except (ValueError, model.DoesNotExist):
            pass
        return ""


class ImporterColumn(models.Model):
    """
    Import file column description
    """
    importer_type = models.ForeignKey(ImporterType, related_name='columns')
    col_number = models.IntegerField(_(u"Column number"), default=1)
    description = models.TextField(_("Description"), blank=True, null=True)
    regexp_pre_filter = models.ForeignKey("Regexp", blank=True, null=True)
    required = models.BooleanField(_(u"Required"), default=False)

    class Meta:
        verbose_name = _(u"Importer - Column")
        verbose_name_plural = _(u"Importer - Columns")
        ordering = ('importer_type', 'col_number')
        unique_together = ('importer_type', 'col_number')

    def __unicode__(self):
        return u"{} - {}".format(self.importer_type, self.col_number)

    def targets_lbl(self):
        return u', '.join([target.target for target in self.targets.all()])

    def duplicate_fields_lbl(self):
        return u', '.join([dp.field_name
                           for dp in self.duplicate_fields.all()])


class ImporterDuplicateField(models.Model):
    """
    Direct copy of result in other fields
    """
    column = models.ForeignKey(ImporterColumn, related_name='duplicate_fields')
    field_name = models.CharField(_(u"Field name"), blank=True, null=True,
                                  max_length=200)
    force_new = models.BooleanField(_(u"Force creation of new items"),
                                    default=False)
    concat = models.BooleanField(_(u"Concatenate with existing"),
                                 default=False)
    concat_str = models.CharField(_(u"Concatenate character"), max_length=5,
                                  blank=True, null=True)

    class Meta:
        verbose_name = _(u"Importer - Duplicate field")
        verbose_name_plural = _(u"Importer - Duplicate fields")


class Regexp(models.Model):
    name = models.CharField(_(u"Name"), max_length=100)
    description = models.CharField(_(u"Description"), blank=True, null=True,
                                   max_length=500)
    regexp = models.CharField(_(u"Regular expression"), max_length=500)

    class Meta:
        verbose_name = _(u"Importer - Regular expression")
        verbose_name_plural = _(u"Importer - Regular expressions")

    def __unicode__(self):
        return self.name


class ImportTarget(models.Model):
    """
    Ishtar database target for a column
    """
    column = models.ForeignKey(ImporterColumn, related_name='targets')
    target = models.CharField(u"Target", max_length=500)
    regexp_filter = models.ForeignKey("Regexp", blank=True, null=True)
    formater_type = models.ForeignKey("FormaterType")
    force_new = models.BooleanField(_(u"Force creation of new items"),
                                    default=False)
    concat = models.BooleanField(_(u"Concatenate with existing"),
                                 default=False)
    concat_str = models.CharField(_(u"Concatenate character"), max_length=5,
                                  blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)

    class Meta:
        verbose_name = _(u"Importer - Target")
        verbose_name_plural = _(u"Importer - Targets")

    def __unicode__(self):
        return self.target[:50] if self.target else self.comment

    @property
    def associated_model(self):
        try:
            return get_associated_model(
                self.column.importer_type.associated_models,
                self.target.split('__'))
        except KeyError:
            return

    def get_choices(self):
        if self.formater_type.formater_type == 'UnknowType' \
                and self.column.importer_type.slug:
            cls = self.column.importer_type.get_importer_class()
            formt = cls().line_format[self.column.col_number - 1]
            if hasattr(formt.formater, 'choices'):
                return [('', '--' * 8)] + list(formt.formater.choices)
            return [('', '--' * 8)]
        if self.formater_type.formater_type == 'StrToBoolean':
            return [('', '--' * 8),
                    ('True', _(u"True")),
                    ('False', _(u"False"))]
        if not self.associated_model or not hasattr(self.associated_model,
                                                    'get_types'):
            return []
        return self.associated_model.get_types()


class TargetKey(models.Model):
    """
    User's link between import source and ishtar database.
    Also temporary used for GeneralType to point missing link before adding
    them in ItemKey table.
    A targetkey connection can be create to be applied to on particular
    import (associated_import), one particular user (associated_user) or to all
    imports (associated_import and associated_user are empty).
    """
    target = models.ForeignKey(ImportTarget, related_name='keys')
    key = models.TextField(_(u"Key"))
    value = models.TextField(_(u"Value"), blank=True, null=True)
    is_set = models.BooleanField(_(u"Is set"), default=False)
    associated_import = models.ForeignKey('Import', blank=True, null=True)
    associated_user = models.ForeignKey('IshtarUser', blank=True, null=True)

    class Meta:
        unique_together = ('target', 'key', 'associated_user',
                           'associated_import')
        verbose_name = _(u"Importer - Target key")
        verbose_name_plural = _(u"Importer - Targets keys")

    def __unicode__(self):
        return u" - ".join([unicode(self.target), self.key[:50]])

    def column_nb(self):
        # for the admin
        return self.target.column.col_number

    def importer_type(self):
        # for the admin
        return self.target.column.importer_type.name

    def format(self):
        if not self.is_set:
            return None
        if self.target.formater_type.formater_type == 'StrToBoolean':
            if self.value in ('False', '0'):
                return False
            elif self.value:
                return True
            return
        return self.value

    def save(self, *args, **kwargs):
        obj = super(TargetKey, self).save(*args, **kwargs)
        if not self.value:
            return obj
        associated_model = self.target.associated_model
        if associated_model and hasattr(self.target.associated_model,
                                        "add_key"):
            v = None
            # pk is given
            try:
                v = self.target.associated_model.objects.get(
                    pk=unicode(int(self.value)))
            except (ValueError, self.target.associated_model.DoesNotExist):
                # try with txt_idx
                try:
                    v = self.target.associated_model.objects.get(
                        txt_idx=unicode(self.value))
                except (self.target.associated_model.DoesNotExist):
                    pass
            if v:
                v.add_key(self.key)
        return obj

TARGET_MODELS = [
    ('OrganizationType', _(u"Organization type")),
    ('SourceType', _(u"Source type")),
    ('AuthorType', _(u"Author type")),
    ('Format', _(u"Format")),
    ('archaeological_operations.models.OperationType', _(u"Operation type")),
    ('archaeological_operations.models.Period', _(u"Period")),
    ('archaeological_context_records.models.Unit', _(u"Unit")),
    ('archaeological_finds.models.MaterialType', _(u"Material")),
    ('archaeological_finds.models.ConservatoryState',
     _(u"Conservatory state")),
    ('archaeological_finds.models.PreservationType', _(u"Preservation type")),
    ('archaeological_finds.models.ObjectType', _(u"Object type")),
    ('archaeological_context_records.models.IdentificationType',
     _("Identification type")),
    ('archaeological_context_records.models.RelationType',
     _(u"Context record relation type")),
    ('SupportType', _(u"Support type")),
]

TARGET_MODELS_KEYS = [tm[0] for tm in TARGET_MODELS]

IMPORTER_TYPES = (
    ('IntegerFormater', _(u"Integer")),
    ('FloatFormater', _(u"Float")),
    ('UnicodeFormater', _(u"String")),
    ('DateFormater', _(u"Date")),
    ('TypeFormater', _(u"Type")),
    ('YearFormater', _(u"Year")),
    ('StrToBoolean', _(u"String to boolean")),
    ('FileFormater', pgettext_lazy("filesystem", u"File")),
    ('UnknowType', _(u"Unknow type"))
)

IMPORTER_TYPES_DCT = {
    'IntegerFormater': IntegerFormater,
    'FloatFormater': FloatFormater,
    'UnicodeFormater': UnicodeFormater,
    'DateFormater': DateFormater,
    'TypeFormater': TypeFormater,
    'YearFormater': YearFormater,
    'StrToBoolean': StrToBoolean,
    'FileFormater': FileFormater,
    'UnknowType': None,
}

DATE_FORMATS = (
    ('%Y', _(u"4 digit year. e.g.: \"2015\"")),
    ('%Y/%m/%d', _(u"4 digit year/month/day. e.g.: \"2015/02/04\"")),
    ('%d/%m/%Y', _(u"Day/month/4 digit year. e.g.: \"04/02/2015\"")),
)

IMPORTER_TYPES_CHOICES = {'TypeFormater': TARGET_MODELS,
                          'DateFormater': DATE_FORMATS}


class FormaterType(models.Model):
    formater_type = models.CharField(u"Formater type", max_length=20,
                                     choices=IMPORTER_TYPES)
    options = models.CharField(_(u"Options"), max_length=500, blank=True,
                               null=True)
    many_split = models.CharField(_(u"Split character(s)"), max_length=10,
                                  blank=True, null=True)

    class Meta:
        verbose_name = _(u"Importer - Formater type")
        verbose_name_plural = _(u"Importer - Formater types")
        unique_together = ('formater_type', 'options', 'many_split')
        ordering = ('formater_type', 'options')

    def __unicode__(self):
        return u" - ".join(
            [unicode(dict(IMPORTER_TYPES)[self.formater_type])
             if self.formater_type in IMPORTER_TYPES_DCT else ''] +
            [getattr(self, k) for k in ('options', 'many_split')
             if getattr(self, k)])

    def get_choices(self):
        if self.format_type in IMPORTER_TYPES_CHOICES:
            return IMPORTER_TYPES_CHOICES[self.format_type]

    def get_formater_type(self, target):
        if self.formater_type not in IMPORTER_TYPES_DCT.keys():
            return
        kwargs = {'db_target': target}
        if self.many_split:
            kwargs['many_split'] = self.many_split
        if self.formater_type == 'TypeFormater':
            if self.options not in TARGET_MODELS_KEYS:
                print('%s not in TARGET_MODELS_KEYS' % self.options)
                return
            model = None
            if self.options in dir():
                model = dir()[self.options]
            else:
                model = import_class(self.options)
            return TypeFormater(model, **kwargs)
        elif self.formater_type == 'UnicodeFormater':
            if self.options:
                try:
                    return UnicodeFormater(int(self.options.strip()), **kwargs)
                except ValueError:
                    pass
            return UnicodeFormater(**kwargs)
        elif self.formater_type == 'DateFormater':
            return DateFormater(self.options, **kwargs)
        elif self.formater_type == 'StrToBoolean':
            return StrToBoolean(**kwargs)
        elif self.formater_type == 'UnknowType':
            return
        else:
            return IMPORTER_TYPES_DCT[self.formater_type](**kwargs)

IMPORT_STATE = (("C", _(u"Created")),
                ("AP", _(u"Analyse in progress")),
                ("A", _(u"Analysed")),
                ("P", _(u"Import pending")),
                ("IP", _(u"Import in progress")),
                ("FE", _(u"Finished with errors")),
                ("F", _(u"Finished")),
                ("AC", _(u"Archived")),
                )

IMPORT_STATE_DCT = dict(IMPORT_STATE)
ENCODINGS = [(settings.ENCODING, settings.ENCODING),
             (settings.ALT_ENCODING, settings.ALT_ENCODING),
             ('utf-8', 'utf-8')]


class Import(models.Model):
    user = models.ForeignKey('IshtarUser')
    importer_type = models.ForeignKey(ImporterType)
    imported_file = models.FileField(_(u"Imported file"),
                                     upload_to="upload/imports/")
    imported_images = models.FileField(
        _(u"Associated images (zip file)"), upload_to="upload/imports/",
        blank=True, null=True)
    encoding = models.CharField(_(u"Encoding"), choices=ENCODINGS,
                                default='utf-8', max_length=15)
    skip_lines = models.IntegerField(_(u"Skip lines"), default=1)
    error_file = models.FileField(_(u"Error file"),
                                  upload_to="upload/imports/",
                                  blank=True, null=True)
    result_file = models.FileField(_(u"Result file"),
                                   upload_to="upload/imports/",
                                   blank=True, null=True)
    match_file = models.FileField(_(u"Match file"),
                                  upload_to="upload/imports/",
                                  blank=True, null=True)
    state = models.CharField(_(u"State"), max_length=2, choices=IMPORT_STATE,
                             default='C')
    conservative_import = models.BooleanField(
        _(u"Conservative import"), default=False,
        help_text='If set to true, do not overload existing values')
    creation_date = models.DateTimeField(_(u"Creation date"),
                                         auto_now_add=True, blank=True,
                                         null=True)
    end_date = models.DateTimeField(_(u"End date"), blank=True,
                                    null=True, editable=False)
    seconds_remaining = models.IntegerField(_(u"Remaining seconds"),
                                            blank=True, null=True,
                                            editable=False)

    class Meta:
        verbose_name = _(u"Import")
        verbose_name_plural = _(u"Imports")

    def __unicode__(self):
        return u"%s - %s - %d" % (unicode(self.importer_type),
                                  unicode(self.user), self.pk)

    def need_matching(self):
        return bool(TargetKey.objects.filter(associated_import=self,
                                             is_set=False).count())

    def get_actions(self):
        """
        Get available action relevant with the current status
        """
        actions = []
        if self.state == 'C':
            actions.append(('A', _(u"Analyse")))
        if self.state == 'A':
            actions.append(('A', _(u"Re-analyse")))
            actions.append(('I', _(u"Launch import")))
        if self.state in ('F', 'FE'):
            actions.append(('A', _(u"Re-analyse")))
            actions.append(('I', _(u"Re-import")))
            actions.append(('AC', _(u"Archive")))
        if self.state == 'AC':
            actions.append(('A', _(u"Unarchive")))
        actions.append(('D', _(u"Delete")))
        return actions

    @property
    def imported_filename(self):
        return self.imported_file.name.split(os.sep)[-1]

    @property
    def status(self):
        if self.state not in IMPORT_STATE_DCT:
            return ""
        return IMPORT_STATE_DCT[self.state]

    def get_importer_instance(self):
        return self.importer_type.get_importer_class()(
            skip_lines=self.skip_lines, import_instance=self,
            conservative_import=self.conservative_import)

    @property
    def data_table(self):
        imported_file = self.imported_file.path
        tmpdir = None
        if zipfile.is_zipfile(imported_file):
            z = zipfile.ZipFile(imported_file)
            filename = None
            for name in z.namelist():
                # get first CSV file found
                if name.endswith('.csv'):
                    filename = name
                    break
            if not filename:
                return []
            tmpdir = tempfile.mkdtemp(prefix='tmp-ishtar-')
            imported_file = z.extract(filename, tmpdir)

        with open(imported_file) as csv_file:
            encodings = [self.encoding]
            encodings += [coding for coding, c in ENCODINGS]
            for encoding in encodings:
                try:
                    vals = [line
                            for line in unicodecsv.reader(csv_file,
                                                          encoding=encoding)]
                    if tmpdir:
                        shutil.rmtree(tmpdir)
                    return vals
                except UnicodeDecodeError:
                    if encoding != encodings[-1]:
                        csv_file.seek(0)
        if tmpdir:
            shutil.rmtree(tmpdir)
        return []

    def initialize(self):
        self.state = 'AP'
        self.save()
        self.get_importer_instance().initialize(self.data_table, output='db')
        self.state = 'A'
        self.save()

    def importation(self):
        self.state = 'IP'
        self.save()
        importer = self.get_importer_instance()
        importer.importation(self.data_table)
        # result file
        filename = slugify(self.importer_type.name)
        now = datetime.datetime.now().isoformat('-').replace(':', '')
        result_file = filename + "_result_%s.csv" % now
        result_file = os.sep.join([self.result_file.storage.location,
                                   result_file])
        with open(result_file, 'w') as fle:
            fle.write(importer.get_csv_result().encode('utf-8'))
        self.result_file = File(open(fle.name))
        if importer.errors:
            self.state = 'FE'
            error_file = filename + "_errors_%s.csv" % now
            error_file = os.sep.join([self.error_file.storage.location,
                                      error_file])
            with open(error_file, 'w') as fle:
                fle.write(importer.get_csv_errors().encode('utf-8'))
            self.error_file = File(open(fle.name))
        else:
            self.state = 'F'
            self.error_file = None
        if importer.match_table:
            match_file = filename + "_match_%s.csv" % now
            match_file = os.sep.join([self.match_file.storage.location,
                                      match_file])
            with open(match_file, 'w') as fle:
                fle.write(importer.get_csv_matches().encode('utf-8'))
            self.match_file = File(open(fle.name))
        self.save()

    def archive(self):
        self.state = 'AC'
        self.save()

    def get_all_imported(self):
        imported = []
        for related, zorg in \
                self._meta.get_all_related_m2m_objects_with_model():
            accessor = related.get_accessor_name()
            imported += [(accessor, obj)
                         for obj in getattr(self, accessor).all()]
        return imported


def pre_delete_import(sender, **kwargs):
    # deleted imported items when an import is delete
    instance = kwargs.get('instance')
    if not instance:
        return
    to_delete = []
    for accessor, imported in instance.get_all_imported():
        to_delete.append(imported)
    for item in to_delete:
        item.delete()


pre_delete.connect(pre_delete_import, sender=Import)


class Organization(Address, Merge, OwnPerms, ValueGetter):
    TABLE_COLS = ('name', 'organization_type',)
    name = models.CharField(_(u"Name"), max_length=500)
    organization_type = models.ForeignKey(OrganizationType,
                                          verbose_name=_(u"Type"))
    history = HistoricalRecords()

    class Meta:
        verbose_name = _(u"Organization")
        verbose_name_plural = _(u"Organizations")
        permissions = (
            ("view_organization", ugettext(u"Can view all Organizations")),
            ("view_own_organization", ugettext(u"Can view own Organization")),
            ("add_own_organization", ugettext(u"Can add own Organization")),
            ("change_own_organization",
             ugettext(u"Can change own Organization")),
            ("delete_own_organization",
             ugettext(u"Can delete own Organization")),
        )

    def simple_lbl(self):
        if self.name:
            return self.name
        return u"{} - {}".format(self.organization_type,
                                 self.town or "")

    def __unicode__(self):
        if self.name:
            return self.name
        return u"{} - {} - {}".format(self.organization_type,
                                      self.address or "",
                                      self.town or "")

    def generate_merge_key(self):
        self.merge_key = slugify(self.name if self.name else '')
        if not self.merge_key:
            self.merge_key = self.EMPTY_MERGE_KEY
        if self.town:
            self.merge_key += "-" + slugify(self.town or '')
        if self.address:
            self.merge_key += "-" + slugify(self.address or '')

    @property
    def associated_filename(self):
        values = [unicode(getattr(self, attr))
                  for attr in ('organization_type', 'name')
                  if getattr(self, attr)]
        return slugify(u"-".join(values))


class PersonType(GeneralType):
    # rights = models.ManyToManyField(WizardStep, verbose_name=_(u"Rights"))
    groups = models.ManyToManyField(Group, verbose_name=_(u"Groups"),
                                    blank=True, null=True)

    class Meta:
        verbose_name = _(u"Person type")
        verbose_name_plural = _(u"Person types")
        ordering = ('label',)


class Person(Address, Merge, OwnPerms, ValueGetter):
    _prefix = 'person_'
    TYPE = (
        ('Mr', _(u'Mr')),
        ('Ms', _(u'Miss')),
        ('Mr and Miss', _(u'Mr and Mrs')),
        ('Md', _(u'Mrs')),
        ('Dr', _(u'Doctor')),
    )
    TABLE_COLS = ('name', 'surname', 'raw_name', 'email', 'person_types_list',
                  'attached_to')
    SHOW_URL = 'show-person'
    MODIFY_URL = 'person_modify'
    title = models.CharField(_(u"Title"), max_length=100, choices=TYPE,
                             blank=True, null=True)
    surname = models.CharField(_(u"Surname"), max_length=50, blank=True,
                               null=True)
    name = models.CharField(_(u"Name"), max_length=200, blank=True,
                            null=True)
    raw_name = models.CharField(_(u"Raw name"), max_length=300, blank=True,
                                null=True)
    contact_type = models.CharField(_(u"Contact type"), max_length=300,
                                    blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    person_types = models.ManyToManyField(PersonType, verbose_name=_(u"Types"))
    attached_to = models.ForeignKey(
        'Organization', related_name='members', on_delete=models.SET_NULL,
        verbose_name=_(u"Is attached to"), blank=True, null=True)

    class Meta:
        verbose_name = _(u"Person")
        verbose_name_plural = _(u"Persons")
        permissions = (
            ("view_person", ugettext(u"Can view all Persons")),
            ("view_own_person", ugettext(u"Can view own Person")),
            ("add_own_person", ugettext(u"Can add own Person")),
            ("change_own_person", ugettext(u"Can change own Person")),
            ("delete_own_person", ugettext(u"Can delete own Person")),
        )

    def simple_lbl(self):
        values = [unicode(getattr(self, attr)) for attr in ('surname', 'name')
                  if getattr(self, attr)]
        if not values and self.raw_name:
            values = [self.raw_name]
        return u" ".join(values)

    def __unicode__(self):
        values = [unicode(getattr(self, attr)) for attr in ('surname', 'name')
                  if getattr(self, attr)]
        if not values and self.raw_name:
            values = [self.raw_name]
        if self.attached_to:
            attached_to = unicode(self.attached_to)
            if values:
                values.append(u'-')
            values.append(attached_to)
        return u" ".join(values)

    def get_values(self, prefix=''):
        values = super(Person, self).get_values(prefix=prefix)
        title = ''
        TYPES = dict(self.TYPE)
        if self.title in TYPES:
            title = dict(self.TYPE)[self.title]
        values[prefix + 'title'] = title
        if not self.attached_to:
            values.update(
                Person.get_empty_values(prefix=prefix + 'attached_to_'))
        return values

    person_types_list_lbl = _(u"Types")

    @property
    def person_types_list(self):
        return u", ".join([unicode(pt) for pt in self.person_types.all()])

    def generate_merge_key(self):
        if self.name and self.name.strip():
            self.merge_key = slugify(self.name.strip()) + \
                ((u'-' + slugify(self.surname.strip()))
                 if self.surname else u'')
        elif self.raw_name and self.raw_name.strip():
            self.merge_key = slugify(self.raw_name.strip())
        elif self.attached_to:
            self.merge_key = self.attached_to.merge_key
        else:
            self.merge_key = self.EMPTY_MERGE_KEY
        if self.merge_key != self.EMPTY_MERGE_KEY and self.attached_to:
            self.merge_key += "-" + self.attached_to.merge_key

    def is_natural(self):
        return not self.attached_to

    def has_right(self, right_name, session=None):
        if '.' in right_name:
            right_name = right_name.split('.')[-1]
        res, cache_key = "", ""
        if session:
            cache_key = 'session-{}-{}'.format(session.session_key, right_name)
            res = cache.get(cache_key)
            if res in (True, False):
                return res

        if type(right_name) in (list, tuple):
            res = bool(self.person_types.filter(
                txt_idx__in=right_name).count()) or \
                bool(self.person_types.filter(
                     groups__permissions__codename__in=right_name).count()) or\
                bool(self.ishtaruser.filter(
                     groups__permissions__codename__in=right_name
                     ).count()) or\
                bool(self.ishtaruser.filter(
                     user_permissions__codename__in=right_name).count())
        # or self.person_types.filter(wizard__url_name__in=right_name).count())
        else:
            res = bool(self.person_types.filter(txt_idx=right_name).count()) or \
                bool(self.person_types.filter(
                     groups__permissions__codename=right_name).count()) or \
                bool(self.ishtaruser.filter(
                     groups__permissions__codename__in=right_name
                     ).count()) or\
                bool(self.ishtaruser.filter(
                     user_permissions__codename__in=right_name).count())
        # or self.person_types.filter(wizard__url_name=right_name).count())
        if session:
            cache.set(cache_key, res, settings.CACHE_SMALLTIMEOUT)
        return res

    def full_label(self):
        values = []
        if self.title:
            values = [unicode(_(self.title))]
        values += [unicode(getattr(self, attr))
                   for attr in ('surname', 'name') if getattr(self, attr)]
        if not values and self.raw_name:
            values = [self.raw_name]
        if self.attached_to:
            values.append(u"- " + unicode(self.attached_to))
        return u" ".join(values)

    @property
    def associated_filename(self):
        values = [unicode(getattr(self, attr))
                  for attr in ('surname', 'name', 'attached_to')
                  if getattr(self, attr)]
        return slugify(u"-".join(values))

    def save(self, *args, **kwargs):
        super(Person, self).save(*args, **kwargs)
        if hasattr(self, 'responsible_town_planning_service'):
            for fle in self.responsible_town_planning_service.all():
                fle.save()  # force update of raw_town_planning_service
        if hasattr(self, 'general_contractor'):
            for fle in self.general_contractor.all():
                fle.save()  # force update of raw_general_contractor


class IshtarUser(User):
    person = models.ForeignKey(Person, verbose_name=_(u"Person"), unique=True,
                               related_name='ishtaruser')

    class Meta:
        verbose_name = _(u"Ishtar user")
        verbose_name_plural = _(u"Ishtar users")

    @classmethod
    def create_from_user(cls, user):
        default = user.username
        surname = user.first_name or default
        name = user.last_name or default
        email = user.email
        person_type = None
        if user.is_superuser:
            ADMINISTRATOR, created = PersonType.objects.get_or_create(
                txt_idx='administrator')
            person_type = ADMINISTRATOR
        else:
            person_type, created = PersonType.objects.get_or_create(
                txt_idx='public_access')
        person = Person.objects.create(title='Mr', surname=surname,
                                       name=name, email=email,
                                       history_modifier=user)
        person.person_types.add(person_type)
        return IshtarUser.objects.create(user_ptr=user, username=default,
                                         person=person)

    def has_right(self, right_name, session=None):
        return self.person.has_right(right_name, session=session)

    def full_label(self):
        return self.person.full_label()

    def has_perm(self, perm, model=None, session=None, obj=None):
        if not session:
            return super(IshtarUser, self).has_perm(perm, model)
        cache_key = 'usersession-{}-{}'.format(session.session_key, perm,
                                               model or 'no')
        res = cache.get(cache_key)
        if res in (True, False):
            return res
        res = super(IshtarUser, self).has_perm(perm, obj)
        cache.set(cache_key, res, settings.CACHE_SMALLTIMEOUT)
        return res


class AuthorType(GeneralType):
    class Meta:
        verbose_name = _(u"Author type")
        verbose_name_plural = _(u"Author types")


class Author(models.Model):
    person = models.ForeignKey(Person, verbose_name=_(u"Person"),
                               related_name='author')
    author_type = models.ForeignKey(AuthorType, verbose_name=_(u"Author type"))

    class Meta:
        verbose_name = _(u"Author")
        verbose_name_plural = _(u"Authors")

    def __unicode__(self):
        return unicode(self.person) + settings.JOINT + \
            unicode(self.author_type)

    def related_sources(self):
        return list(self.treatmentsource_related.all()) + \
            list(self.operationsource_related.all()) + \
            list(self.findsource_related.all()) + \
            list(self.contextrecordsource_related.all())


class SourceType(GeneralType):
    class Meta:
        verbose_name = _(u"Source type")
        verbose_name_plural = _(u"Source types")


class SupportType(GeneralType):
    class Meta:
        verbose_name = _(u"Support type")
        verbose_name_plural = _(u"Support types")


class Format(GeneralType):
    class Meta:
        verbose_name = _(u"Format")
        verbose_name_plural = _(u"Formats")


class Source(models.Model):
    title = models.CharField(_(u"Title"), max_length=300)
    external_id = models.CharField(_(u"External ID"), max_length=12, null=True,
                                   blank=True)
    source_type = models.ForeignKey(SourceType, verbose_name=_(u"Type"))
    support_type = models.ForeignKey(SupportType, verbose_name=_(u"Support"),
                                     blank=True, null=True,)
    format_type = models.ForeignKey(Format, verbose_name=_(u"Format"),
                                    blank=True, null=True,)
    scale = models.CharField(_(u"Scale"), max_length=30, null=True,
                             blank=True)
    authors = models.ManyToManyField(Author, verbose_name=_(u"Authors"),
                                     related_name="%(class)s_related")
    associated_url = models.URLField(
        verify_exists=False, blank=True, null=True,
        verbose_name=_(u"Numerical ressource (web address)"))
    receipt_date = models.DateField(blank=True, null=True,
                                    verbose_name=_(u"Receipt date"))
    creation_date = models.DateField(blank=True, null=True,
                                     verbose_name=_(u"Creation date"))
    receipt_date_in_documentation = models.DateField(
        blank=True, null=True,
        verbose_name=_(u"Receipt date in documentation"))
    item_number = models.IntegerField(_(u"Item number"), default=1)
    reference = models.CharField(_(u"Ref."), max_length=100, null=True,
                                 blank=True)
    internal_reference = models.CharField(
        _(u"Internal ref."), max_length=100, null=True, blank=True)
    description = models.TextField(_(u"Description"), blank=True, null=True)
    comment = models.TextField(_(u"Comment"), blank=True, null=True)
    additional_information = models.TextField(_(u"Additional information"),
                                              blank=True, null=True)
    duplicate = models.BooleanField(_(u"Has a duplicate"), default=False)
    TABLE_COLS = ['title', 'source_type', 'authors', ]

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title

    @property
    def associated_filename(self):
        values = [unicode(getattr(self, attr))
                  for attr in ('source_type', 'title')
                  if getattr(self, attr)]
        return slugify(u"-".join(values))

if settings.COUNTRY == 'fr':
    class Arrondissement(models.Model):
        name = models.CharField(u"Nom", max_length=30)
        department = models.ForeignKey(Department, verbose_name=u"Département")

        def __unicode__(self):
            return settings.JOINT.join((self.name, unicode(self.department)))

    class Canton(models.Model):
        name = models.CharField(u"Nom", max_length=30)
        arrondissement = models.ForeignKey(Arrondissement,
                                           verbose_name=u"Arrondissement")

        def __unicode__(self):
            return settings.JOINT.join(
                (self.name, unicode(self.arrondissement)))


class Town(models.Model):
    name = models.CharField(_(u"Name"), max_length=100)
    surface = models.IntegerField(_(u"Surface (m2)"), blank=True, null=True)
    center = models.PointField(_(u"Localisation"), srid=settings.SRID,
                               blank=True, null=True)
    if settings.COUNTRY == 'fr':
        numero_insee = models.CharField(u"Numéro INSEE", max_length=6,
                                        unique=True)
        departement = models.ForeignKey(
            Department, verbose_name=u"Département", null=True, blank=True)
        canton = models.ForeignKey(Canton, verbose_name=u"Canton", null=True,
                                   blank=True)
    objects = models.GeoManager()

    class Meta:
        verbose_name = _(u"Town")
        verbose_name_plural = _(u"Towns")
        if settings.COUNTRY == 'fr':
            ordering = ['numero_insee']

    def __unicode__(self):
        if settings.COUNTRY == "fr":
            return u"%s (%s)" % (self.name, self.numero_insee[:2])
        return self.name


class OperationType(GeneralType):
    order = models.IntegerField(_(u"Order"), default=1)
    preventive = models.BooleanField(_(u"Is preventive"), default=True)

    class Meta:
        verbose_name = _(u"Operation type")
        verbose_name_plural = _(u"Operation types")
        ordering = ['-preventive', 'order', 'label']

    @classmethod
    def get_types(cls, dct={}, instances=False, exclude=[], empty_first=True,
                  default=None):
        tuples = []
        dct['available'] = True
        if not instances and empty_first and not default:
            tuples.append(('', '--'))
        if default:
            try:
                default = cls.objects.get(txt_idx=default)
                tuples.append((default.pk, _(unicode(default))))
            except cls.DoesNotExist:
                pass
        items = cls.objects.filter(**dct)
        if default:
            exclude.append(default.txt_idx)
        if exclude:
            items = items.exclude(txt_idx__in=exclude)
        current_preventive, current_lst = None, None
        for item in items.order_by(*cls._meta.ordering).all():
            if not current_lst or item.preventive != current_preventive:
                if current_lst:
                    tuples.append(current_lst)
                current_lst = [_(u"Preventive") if item.preventive else
                               _(u"Research"), []]
                current_preventive = item.preventive
            current_lst[1].append((item.pk, _(unicode(item))))
        if current_lst:
            tuples.append(current_lst)
        return tuples

    @classmethod
    def is_preventive(cls, ope_type_id, key=''):
        try:
            op_type = cls.objects.get(pk=ope_type_id)
        except cls.DoesNotExist:
            return False
        if not key:
            return op_type.preventive
        return key == op_type.txt_idx
