# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from ..models import CREATED, ERROR, DESTROYING
from django.utils.html import format_html

class DatabaseInfraInstanceBindAdmin(admin.ModelAdmin):
    search_fields = ("databaseinfra__name","bind_address",)
    list_filter = ("bind_status",)
    list_display = ("databaseinfra", "instance", "instance_port", "bind_address", "friendly_bind_status")

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

