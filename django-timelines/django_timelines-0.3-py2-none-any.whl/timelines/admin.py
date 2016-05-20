# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin.widgets import ForeignKeyRawIdWidget
from django.contrib.contenttypes.models import ContentType
from ckeditor.widgets import CKEditorWidget
from contentrelations.generic import GenericRawIdWidget
from concepts.admin import ConceptItemInline

from .models import Timeline, Era, Slide, TimelineSlide
from .fields import ForeignKeyRawIdWidgetWrapper


class EraAdmin(admin.ModelAdmin):
    """
    Era
    """
    model = Era


class SlideAdmin(admin.ModelAdmin):
    list_display = ('media_obj', 'obj_headline')
    raw_id_fields = ('background_image', )
    search_fields = ['headline_ovr', 'caption_ovr', 'credit_ovr', 'text_ovr']
    fieldsets = (
        ('Date Information', {
            'fields': (('start_date', 'start_time'), ('end_date', 'end_time'), )
        }),
        ('Media URL', {
            'fields': ('url', ('content_type', 'object_id')),
            'description': "Either set the URL or select the content type and object",
        }),
        ('Slide Content', {
            'fields': ('headline_ovr', 'text_ovr', 'caption_ovr', 'credit_ovr'),
            'description': "These fields will override the values for related objects"
        }),
        ('Background', {
            'fields': ('use_media_as_background', 'background_image', 'background_color')
        })
    )

    class Media:
        js = ("timelines/timeline_admin.js",)

    def media_obj(self, obj):
        if obj.url:
            return u"URL: %s" % obj.url
        else:
            return u"Object: %s" % obj.content_object

    def obj_headline(self, obj):
        return obj.headline

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from .registration import registry

        if db_field.name == "content_type":
            ctype_ids = [ContentType.objects.get_for_model(x).id for x in registry._registry]

            kwargs['limit_choices_to'] = {'pk__in': ctype_ids}
        return super(SlideAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(SlideAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'object_id':
            formfield.widget = GenericRawIdWidget()
        if db_field.name in ('headline_ovr', 'text_ovr', 'caption_ovr', 'credit_ovr'):
            formfield.widget = CKEditorWidget()

        return formfield

    def get_adapter_fields(self, request, content_type_id, object_id):
        """
        Return a JSON object including the adapter fields for the object
        """
        from django.contrib.contenttypes.models import ContentType
        from .registration import registry
        from django.http import JsonResponse

        ctype = ContentType.objects.get_for_id(int(content_type_id))
        obj = ctype.get_object_for_this_type(id=int(object_id))
        adapter = registry.adapter_for_instance(obj)
        return JsonResponse({
            'caption': adapter.caption,
            'clickthrough_url': adapter.clickthrough_url,
            'credit': adapter.credit,
            'headline': adapter.headline,
            'media_url': adapter.media_url,
            'text': adapter.text,
            'thumbnail': adapter.thumbnail
        })

    def get_urls(self):
        from django.conf.urls import url
        urls = super(SlideAdmin, self).get_urls()
        my_urls = [
            url(r'^adapter_fields/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', self.get_adapter_fields),
        ]
        return my_urls + urls


class SlideInline(admin.TabularInline):
    model = TimelineSlide
    verbose_name = "Slide"
    verbose_name_plural = "Slides"
    raw_id_fields = ('slide', )
    fields = ('slide', 'group', 'order')
    extra = 0

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(SlideInline, self).formfield_for_dbfield(db_field, **kwargs)
        if (formfield and isinstance(formfield.widget, ForeignKeyRawIdWidget)):
            widget = ForeignKeyRawIdWidgetWrapper(formfield.widget)
            formfield.widget = widget
        return formfield


class TimelineAdmin(admin.ModelAdmin):
    """
    Admin for Timeline
    """
    tabs = {
        'Overview': 0,
        'Media URL': 0,
        'Title Slide': 0,
        'Background': 0,
        'Publishing': 1,
    }
    save_on_top = True
    list_display = ('headline_ovr',)
    # list_filter = ('',)
    inlines = [
        SlideInline,
        ConceptItemInline,
    ]
    raw_id_fields = ('background_image', 'credits', )
    search_fields = ['headline_ovr', 'caption_ovr', 'credit_ovr', 'text_ovr']
    prepopulated_fields = {'slug': ('headline_ovr',)}
    readonly_fields = ('publish_date', )
    fieldsets = (
        ('Overview', {
            'fields': ('description', 'content', 'scale', 'eras', 'credits'),
            'classes': [],
        }),
        ('Media URL', {
            'fields': ('url', ('content_type', 'object_id')),
            'description': "Either set the URL or select the content type and object",
        }),
        ('Title Slide', {
            'fields': ('headline_ovr', 'slug', 'text_ovr', 'caption_ovr', 'credit_ovr'),
            'description': "These fields will override the values for related objects",
            'classes': ['collapse', ],
        }),
        ('Background', {
            'fields': ('use_media_as_background', 'background_image', 'background_color'),
            'classes': ['collapse', ],
        }),
        ('Publishing', {
            'fields': ('published', 'publish_date'),
            'classes': [],
        })
    )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        from .registration import registry

        if db_field.name == "content_type":
            ctype_ids = [ContentType.objects.get_for_model(x).id for x in registry._registry]

            kwargs['limit_choices_to'] = {'pk__in': ctype_ids}
        return super(TimelineAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(TimelineAdmin, self).formfield_for_dbfield(db_field, **kwargs)

        if db_field.name == 'object_id':
            formfield.widget = GenericRawIdWidget()

        if db_field.name in ('content', 'headline_ovr', 'text_ovr',
                             'caption_ovr', 'credit_ovr'):
            formfield.widget = CKEditorWidget()

        return formfield

    def get_adapter_fields(self, request, content_type_id, object_id):
        """
        Return a JSON object including the adapter fields for the object
        """
        from django.contrib.contenttypes.models import ContentType
        from .registration import registry
        from django.http import JsonResponse

        ctype = ContentType.objects.get_for_id(int(content_type_id))
        obj = ctype.get_object_for_this_type(id=int(object_id))
        adapter = registry.adapter_for_instance(obj)
        return JsonResponse({
            'caption': adapter.caption,
            'clickthrough_url': adapter.clickthrough_url,
            'credit': adapter.credit,
            'headline': adapter.headline,
            'media_url': adapter.media_url,
            'text': adapter.text,
            'thumbnail': adapter.thumbnail
        })

    def get_urls(self):
        from django.conf.urls import url
        urls = super(TimelineAdmin, self).get_urls()
        my_urls = [
            url(r'^adapter_fields/(?P<content_type_id>\d+)/(?P<object_id>\d+)/$', self.get_adapter_fields),
        ]
        return my_urls + urls

    class Media:
        js = ("timelines/timeline_admin.js",)


admin.site.register(Timeline, TimelineAdmin)
admin.site.register(Slide, SlideAdmin)
admin.site.register(Era, EraAdmin)
