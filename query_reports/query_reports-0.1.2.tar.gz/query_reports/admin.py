from django.contrib import admin
from .models import ReportColumn, ReportFilter, ReportVariable, QueryReport


class ReportVariable_Inline(admin.TabularInline):
    model = ReportVariable
    extra = 0


class ReportFilter_Inline(admin.TabularInline):
    model = ReportFilter
    extra = 0


class ReportColumn_Inline(admin.TabularInline):
    model = ReportColumn


class QueryReportOptions(admin.ModelAdmin):
    search_fields = ["name"]
    inlines = [
        ReportVariable_Inline,
        ReportFilter_Inline,
        ReportColumn_Inline
    ]
    prepopulated_fields = {"slug": ["name"]}


admin.site.register(QueryReport, QueryReportOptions)
