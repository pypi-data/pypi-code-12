from django.db import models


class AbstractAuthSchBase(models.Model):
    auth_sch_internal_id = models.CharField(max_length=100, unique=True, blank=True)
    access_token = models.CharField(max_length=100, unique=True, blank=True)
    refresh_token = models.CharField(max_length=100, unique=True, blank=True)

    class Meta:
        abstract = True
