from django.conf import settings

from django.contrib import admin
from django.forms.fields import CharField
from django.forms.widgets import Textarea

from .models import *


class SnippetAdmin(admin.ModelAdmin):
    change_form_template = 'content/admin/change_form.html'
    list_display = ('section', 'url', 'publish', 'expire')
    list_editable = ('publish', 'expire')
    search_fields = ('section__name',)
    list_filter = ('section',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "content":
            kwargs['widget'] = Textarea(attrs={"class": 'richcontent'})
        return super(SnippetAdmin, self).formfield_for_dbfield(db_field, **kwargs)


class PageAdmin(admin.ModelAdmin):
    change_form_template = 'content/admin/change_form.html'
    list_display = ('url', 'title')
    list_display_links = ('url', 'title')
    fieldsets = (
        (None, {
            'fields': ('url', 'title', 'content', 'sites')
        }),
        ('Meta', {
            'classes': ('collapse',),
            'fields': ('keywords', 'description',)
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('enable_comments', 'registration_required', 'template_name')
        }),
    )

    def _actions_column(self, page):
        actions = super(PageAdmin, self)._actions_column(page)
        actions.append(u'<a href="add/?parent=%s" title="%s"><img src="%sadmin/img/icon_addlink.gif" alt="%s"></a>' % (
            page.pk, 'Add child page', settings.STATIC_URL, 'Add child page'))
        return actions


admin.site.register(Snippet, SnippetAdmin)
admin.site.register(Page, PageAdmin)
