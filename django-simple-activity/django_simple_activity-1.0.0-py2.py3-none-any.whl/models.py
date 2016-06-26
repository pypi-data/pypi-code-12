from __future__ import unicode_literals

from django.utils import timezone
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.humanize.templatetags.humanize import naturaltime

from . querysets import ActionQueryset


class Action(models.Model):
    # The object which performed the activity
    actor_content_type = models.ForeignKey(
        ContentType, related_name='actor', blank=True, null=True
    )
    actor_object_id = models.CharField(
        max_length=500, blank=True, null=True, db_index=True)
    actor = GenericForeignKey('actor_content_type', 'actor_object_id')
    # The phrase describing the action of that activity
    verb = models.CharField(max_length=500)

    # The object which is linked to the action (e.g. liked, favourited)
    action_content_type = models.ForeignKey(
        ContentType, related_name='action', blank=True, null=True
    )
    action_object_id = models.CharField(
        max_length=500, blank=True, null=True, db_index=True)
    action = GenericForeignKey('action_content_type', 'action_object_id')

    # The object on which the action was performed upon (e.g. a fb page)
    target_content_type = models.ForeignKey(
        ContentType, related_name='target', blank=True, null=True
    )
    target_object_id = models.CharField(
        max_length=500, blank=True, null=True, db_index=True)
    target = GenericForeignKey('target_content_type', 'target_object_id')

    is_public = models.BooleanField(default=True, db_index=True)
    timestamp = models.DateTimeField(
        default=timezone.now, blank=True, db_index=True)
    objects = ActionQueryset.as_manager()

    @property
    def time_ago(self):
        # human readable time ago, e.g. 5 hours ago
        return naturaltime(self.timestamp).replace('\xa0', ' ')

    class Meta:
        ordering = ('-timestamp', )
        app_label = 'activity'
