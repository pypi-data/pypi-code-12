# coding=utf-8
from django.contrib import admin

from .models import Category, Content


class CmsPageCategoryAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if obj is not None and obj.id == 1:
            return False
        return super(CmsPageCategoryAdmin, self).has_delete_permission(
            request, obj
        )

admin.site.register(Category, CmsPageCategoryAdmin)


class ContentAdmin(admin.ModelAdmin):
    list_display = ('url', 'title', 'publish', 'status', 'link')
    list_filter = ('publish', 'category', 'status', 'author')
    search_fields = ('title', 'url', 'template')
    readonly_fields = ('created_on', 'modified_on')

    def link(self, obj):
        return "<a target='_blank' href='{}'>View on site</a>".format(
            obj.get_absolute_url()
        )
    link.allow_tags = True

admin.site.register(Content, ContentAdmin)
