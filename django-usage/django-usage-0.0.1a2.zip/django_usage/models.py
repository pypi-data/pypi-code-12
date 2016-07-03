# -*- coding: UTF-8 -*-
"""
    Created by Régis Eduardo Crestani <regis.crestani@gmail.com> on 21/06/2016.
"""
from django.db import models
from django.conf import settings

class RequestRawData(models.Model):
    # request
    name = models.CharField(max_length=250)
    method = models.CharField(max_length=10)
    # response
    size = models.BigIntegerField()
    status = models.PositiveSmallIntegerField()
    latency = models.FloatField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, default=None)
    # history
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
