# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from ..models import SUCCESS, ERROR, PENDING
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

class AclApiJobAdmin(admin.ModelAdmin):
    search_fields = ("database__name", "job_id", "job_operation",)
    list_filter = ("database", "environment", "job_id", "job_status", "job_operation", )
    list_display = ( "database", "friendly_job_status", "job_operation", "environment", "created_dt_format")
    actions = None
    readonly_fields = ("database", "environment", "job_id", "job_status", "job_operation",)
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
        super(AclApiJobAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )


    def created_dt_format(self, database):
        return database.created_at.strftime("%b. %d, %Y") or ""

    created_dt_format.short_description = "Created at"
    created_dt_format.admin_order_field = "created_at"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def friendly_job_status(self, job):

        html_default = '<span class="label label-{}">{}</span>'

        if job.job_status == SUCCESS:
            status = html_default.format("success", "Success")
        elif job.job_status == ERROR:
            status = html_default.format("important", "Error")
        elif job.job_status == PENDING:
            status = html_default.format("warning", "Pending")
        else:
            status = html_default.format("info", "Running")

        return format_html(status)

    friendly_job_status.short_description = "Job Status"
    friendly_job_status.admin_order_field = "job_status"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user.username
            obj.save()
