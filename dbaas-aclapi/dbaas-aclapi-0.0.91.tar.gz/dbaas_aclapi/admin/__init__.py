# -*- coding:utf-8 -*-
from django.contrib import admin
from .database_bind import DatabaseBindAdmin
from .acl_api_job import AclApiJobAdmin
from .database_infra_instance_bind import DatabaseInfraInstanceBindAdmin
from .. import models

admin.site.register(models.DatabaseBind, DatabaseBindAdmin)
admin.site.register(models.AclApiJob, AclApiJobAdmin)
admin.site.register(models.DatabaseInfraInstanceBind, DatabaseInfraInstanceBindAdmin)

