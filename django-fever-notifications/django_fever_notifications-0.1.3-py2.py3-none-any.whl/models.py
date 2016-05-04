# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals, print_function

import uuid
import itertools
from django.utils.encoding import python_2_unicode_compatible
from django.db import models, DEFAULT_DB_ALIAS
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models.query import QuerySet
from django.contrib.admin.utils import NestedObjects


def get_related_objects(obj, using=DEFAULT_DB_ALIAS):
    # This code is based on https://github.com/makinacorpus/django-safedelete
    collector = NestedObjects(using=using)
    collector.collect([obj])

    def flatten(elem):
        if isinstance(elem, list):
            return itertools.chain.from_iterable(map(flatten, elem))
        elif obj != elem:
            return (elem,)
        return ()

    return flatten(collector.nested())


class NotificationManager(models.Manager):

    def get_queryset(self):
        if self.model:
            return super(NotificationManager, self).get_queryset().exclude(
                status=self.model.DELETED
            )

    def by_target(self, target):
        if self.model:
            return super(NotificationManager, self).get_queryset().filter(
                target_content_type=ContentType.objects.get_for_model(target),
                target_id=target.id
            )

    def all_with_deleted(self):
        if self.model:
            return QuerySet(self.model, using=self._db).all()

    def only_deleted(self):
        if self.model:
            return QuerySet(self.model, using=self._db).filter(status=self.model.DELETED)


@python_2_unicode_compatible
class Notification(models.Model):
    """
    Generic notification class
    """

    UNREAD = 'U'
    READ = 'R'
    DELETED = 'D'
    STATUS_CHOICES = (
        (UNREAD, _('Unread')),
        (READ, _('Read')),
        (DELETED, _('Deleted')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, db_index=True, blank=True)
    title = models.CharField(max_length=50)
    message = models.TextField(blank=True)

    target_content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('target object'),
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    target_id = models.PositiveIntegerField(
        verbose_name=_('related object'),
        null=True,
    )
    target = GenericForeignKey('target_content_type', 'target_id')
    status = models.CharField(choices=STATUS_CHOICES, default=UNREAD, max_length=50, db_index=True)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expiration = models.DateTimeField(null=True, blank=True, db_index=True)

    objects = NotificationManager()

    class Meta:
        ordering = ['-created_at']

    def delete(self):
        # Fetch related models
        to_delete = get_related_objects(self)

        for obj in to_delete:
            obj.delete()

        # Soft delete the object
        self.status = self.DELETED
        self.save()

    def __str__(self):
        return "<Notification {}> {} - {}".format(self.id, self.code, self.title)
