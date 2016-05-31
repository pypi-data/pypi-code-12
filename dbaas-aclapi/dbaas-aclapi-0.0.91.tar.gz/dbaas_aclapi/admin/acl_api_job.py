# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from django.contrib import admin
from ..models import SUCCESS, ERROR, PENDING
from django.utils.html import format_html
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from datetime import datetime
from datetime import timedelta

class IsClosedFilter(SimpleListFilter):
    title = _('Period')

    parameter_name = 'period'

    def lookups(self, request, model_admin):
        return (
            (None, _('Last 30 days')),
            ('all', _('All')),
        )

    def choices(self, cl):
        for lookup, title in self.lookup_choices:
            yield {
                'selected': self.value() == lookup,
                'query_string': cl.get_query_string({
                    self.parameter_name: lookup,
                }, []),
                'display': title,
            }

    def queryset(self, request, queryset):
        last_month = datetime.today() - timedelta(days=30)

        if self.value() == None:
            return queryset.filter(created_at__gte=last_month)

class AclApiJobAdmin(admin.ModelAdmin):
    search_fields = ("database__name", "job_id", "job_operation",)
    list_filter = ("job_status", "job_operation", "environment",
        IsClosedFilter)
    list_display = ( "job_id", "database", "friendly_job_status", "job_operation", "environment", "created_at")
    actions = None
    enable_change_view = False

    def change_view(self, request, object_id, form_url='', extra_context=None):

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

    def queryset(self, request):
        queryset = super(AclApiJobAdmin, self).queryset(request)
        return queryset.select_related('database', 'environment')
