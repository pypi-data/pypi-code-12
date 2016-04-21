from django.db import models
from django.conf import settings

from enumerify import fields

from .enums import LogReason, LogStatus


class Log(models.Model):
    email = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    mandrill_id = models.CharField(max_length=511, blank=True, null=True)
    meta_data = models.TextField()
    status = fields.SelectIntegerField(blueprint=LogStatus, default=LogStatus.DEFAULT, db_index=True)
    reason = fields.SelectIntegerField(blueprint=LogReason, default=LogReason.NA, db_index=True)
    template = models.CharField(max_length=511)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)