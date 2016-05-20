# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from ..models import CREATED, ERROR, DESTROYING
from django.utils.html import format_html

class DatabaseInfraInstanceBindAdmin(admin.ModelAdmin):
    search_fields = ("databaseinfra__name","bind_address",)
    list_filter = ("bind_status",)
    list_display = ("databaseinfra", "instance", "instance_port", "bind_address", "friendly_bind_status")
    actions = None
    enable_change_view = False

    def change_view(self, request, object_id, form_url='', extra_context=None):

        if self.enable_change_view:
            return super(ReportMixin, self).change_view(
                request,
                object_id,
                form_url,
                extra_context
            )
        else:
            from django.core.urlresolvers import reverse
            from django.http import HttpResponseRedirect

            opts = self.model._meta
            url = reverse('admin:{app}_{model}_changelist'.format(
                app=opts.app_label,
                model=opts.model_name,
            ))
            return HttpResponseRedirect(url)

    def __init__(self, *args, **kwargs):
        super(DatabaseInfraInstanceBindAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
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

