# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from ..models import CREATED, ERROR, DESTROYING
from django.utils.html import format_html
from ..models import DatabaseInfraInstanceBind


class DatabaseBindAdmin(admin.ModelAdmin):
    search_fields = ("database__name", "bind_address",)
    list_filter = ("bind_status",)
    list_display = ("database", "bind_address", "friendly_bind_status", "binds_requested", "created_dt_format")
    readonly_fields = ("infra_instance_bind",)

    def infra_instance_bind(self,database):
        html_instances = []
        db_infras = DatabaseInfraInstanceBind.objects.filter(databaseinfra=database.database.databaseinfra, bind_address= database.bind_address)
        for db_infra in db_infras:
                html_instances.append("Address: %s  Port: %d" % (unicode(db_infra.instance), db_infra.instance_port))
        return "<br/>".join(html_instances)
    infra_instance_bind.allow_tags = True
    infra_instance_bind.short_description = "Instances"

    def created_dt_format(self, database):
        return database.created_at.strftime("%b. %d, %Y") or ""

    created_dt_format.short_description = "Created at"
    created_dt_format.admin_order_field = "created_at"

    def has_add_permission(self, request):
        return False

    def friendly_bind_status(self, database):

        html_default = '<span class="label label-{}">{}</span>'

        if database.bind_status == CREATED:
            status = html_default.format("success", "Created")
        elif database.bind_status == ERROR:
            status = html_default.format("important", "Error")
        elif database.bind_status == DESTROYING:
            status = html_default.format("warning", "Destroying")
        else:
            status = html_default.format("info", "Creating")

        return format_html(status)

    friendly_bind_status.short_description = "Bind Status"
