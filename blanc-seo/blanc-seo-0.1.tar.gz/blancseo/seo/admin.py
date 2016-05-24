from django.contrib import admin
from django.contrib.contenttypes.generic import GenericStackedInline
from models import MetaContent, URLMetaContent


class MetaContentInlineAdmin(GenericStackedInline):
    model = MetaContent
    max_num = 1


class URLMetaContentAdmin(admin.ModelAdmin):
    search_fields = ('url',)


admin.site.register(URLMetaContent, URLMetaContentAdmin)
