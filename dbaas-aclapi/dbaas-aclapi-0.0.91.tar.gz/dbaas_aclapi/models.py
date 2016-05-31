# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _
from logical.models import Database
from physical.models import DatabaseInfra, Environment
import simple_audit

ERROR = 0
CREATED = 1
CREATING = 2
DESTROYING = 3

BIND_STATUS = (
    (DESTROYING, 'Destroying'),
    (CREATED, 'Created'),
    (CREATING, 'Creating'),
    (ERROR, 'Error'),
)

SUCCESS = 1
PENDING = 2
RUNNING = 3

JOB_STATUS = (
    (ERROR, 'ERROR'),
    (SUCCESS, 'SUCCESS'),
    (PENDING, 'PENDING'),
    (RUNNING, 'RUNNING'),
)

UNBIND = 0
BIND = 1

JOB_OPERATION = (
    (UNBIND, 'Unbind'),
    (BIND, 'Bind'),
)


def get_description_from_tupple(status_tuple, status):
    return {_tuple[0]: _tuple[1] for _tuple in status_tuple}.get(status, None)


class BaseModel(models.Model):
    """Base model class"""
    created_at = models.DateTimeField(
        verbose_name=_("created_at"), auto_now_add=True)

    updated_at = models.DateTimeField(
        verbose_name=_("updated_at"), auto_now=True)

    class Meta:
        abstract = True

    def __unicode__(self):
        if hasattr(self, 'name'):
            return "%s" % self.name
        elif hasattr(self, '__unicode__'):
            return self.__unicode__()


class DatabaseBind(BaseModel):
    database = models.ForeignKey(
        Database, related_name="acl_binds", on_delete=models.SET_NULL, null=True,
        blank=False, editable=False)

    bind_address = models.GenericIPAddressField(
        verbose_name=_("Bind Address"), null=False, blank=False, editable=False)

    bind_status = models.IntegerField(choices=BIND_STATUS, default=2)

    binds_requested = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = (
            ('database', 'bind_address', )
        )

    def __unicode__(self):
        return "{} access to {}".format(self.bind_address, self.database)


class DatabaseInfraInstanceBind(BaseModel):
    databaseinfra = models.ForeignKey(DatabaseInfra, related_name="acl_binds",)

    instance = models.GenericIPAddressField(
        verbose_name=_("Instance Address"), null=False, blank=False, editable=False)

    instance_port = models.PositiveSmallIntegerField(
        verbose_name=_("Instance Port"), null=False, blank=False, editable=False,)

    bind_address = models.GenericIPAddressField(
        verbose_name=_("Bind Address"), null=False, blank=False, editable=False)

    bind_status = models.IntegerField(choices=BIND_STATUS, default=2)

    class Meta:
        unique_together = (
            ('instance', 'instance_port', 'bind_address', 'databaseinfra')
        )

    def __unicode__(self):
        return "{} access to {}".format(self.bind_address, self.instance)


class AclApiJob(BaseModel):
    job_id = models.PositiveIntegerField(
        verbose_name=_("Job Id"), null=False, blank=False, editable=False, unique=True)

    job_status = models.PositiveSmallIntegerField(
        choices=JOB_STATUS, verbose_name=_("Job Status"), null=False, blank=False, db_index=True)

    job_operation = models.PositiveSmallIntegerField(
        choices=JOB_OPERATION, verbose_name=_("Job Operation"), null=False, blank=False,
        db_index=True, editable=False)

    environment = models.ForeignKey(
        Environment, related_name="aclapi_jobs", on_delete=models.CASCADE, null=False,
        blank=False, editable=False, db_index=True)

    database = models.ForeignKey(
        Database, related_name="acl_jobs", on_delete=models.SET_NULL, null=True,
        blank=False, editable=False, db_index=True)

    def __unicode__(self):
        job_status = get_description_from_tupple(JOB_STATUS, self.job_status)
        job_operation = get_description_from_tupple(JOB_OPERATION, self.job_operation)

        return "AclApi {} job with id {} is {}".format(job_operation, self.job_id, job_status)

    class Meta:
        unique_together = (
            ('job_id', 'job_operation')
        )


simple_audit.register(DatabaseInfraInstanceBind, DatabaseBind, AclApiJob)
