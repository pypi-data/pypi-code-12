from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline

from .models import MetaContent, URLMetaContent


class MetaContentInlineAdmin(GenericStackedInline):
    model = MetaContent
    max_num = 1
    fieldsets = (
        ('HTML', {
            'fields': ('title', 'description', 'keywords')
        }),
        ('Open graph', {
            'fields': (
                'open_graph_url', 'open_graph_title', 'open_graph_description', 'open_graph_image')
        }),
    )


@admin.register(URLMetaContent)
class URLMetaContentAdmin(admin.ModelAdmin):
    search_fields = ('url',)
    list_display = ('url',)
    fieldsets = (
        (None, {
            'fields': ('url',)
        }),
        ('HTML', {
            'fields': ('title', 'description', 'keywords')
        }),
        ('Open graph', {
            'fields': (
                'open_graph_url', 'open_graph_title', 'open_graph_description', 'open_graph_image')
        }),
    )
