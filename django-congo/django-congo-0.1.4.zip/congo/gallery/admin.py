# -*- coding: utf-8 -*-
from congo.admin.actions import make_visible, make_invisible
from congo.admin.filters import ChoicesNoneFieldListFilter
from congo.conf import settings
from congo.utils.classes import BlankImage, get_class
from django import shortcuts
from django.conf.urls import patterns
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from congo.gallery.models import get_watermark_choice

modeladmin_name = settings.CONGO_ADMIN_MODEL
modeladmin = get_class(modeladmin_name)

class PhotoInline(admin.StackedInline):
    fields = ('id', 'title', 'image', 'photo', 'is_visible')
    readonly_fields = ('id', 'photo')
    extra = 0

    def photo(self, obj):
        if obj.image:
            html = obj.image.render(100)
        else:
            html = BlankImage().render(100)
        return """<div class="thumb">%s</div>""" % html
    photo.allow_tags = True
    photo.short_description = u'Podgląd'

class PhotoAdmin(modeladmin):
    list_display = ('id', 'photo_thumb', 'title', 'watermark', 'size', 'is_visible', 'position',)
    list_display_links = ('photo_thumb',)
    list_editable = ('position',)
    list_filter = ('is_visible', ('watermark', ChoicesNoneFieldListFilter))
    fields = ('image', 'title', 'watermark', 'size', 'is_visible', 'photo_preview',)
    readonly_fields = ('size', 'photo_preview')
    search_fields = ('title', 'image')
    actions = (make_visible, make_invisible, 'change_watermark')

#    class Media:
#        js = (
#            '/static/custom_admin/js/jquery-ui.custom.min.js',
#            '/static/custom_admin/js/position.js',
#        )

    def get_urls(self):
        urls = patterns('',
            (r'^(?P<action>(change_watermark))/$', self.action_view)
        )
        return urls + super(PhotoAdmin, self).get_urls()

    # fields
    def photo_thumb(self, obj):
        html = obj.image.render(100)
        return """<span class="thumb">%s</span>""" % html
    photo_thumb.allow_tags = True
    photo_thumb.short_description = _("Photo")

    def photo_preview(self, obj):
        url = obj.image.get_url()
        html = obj.image.render(100)
        return """<span class="thumb"><a href="%s">%s</a></span>""" % (url, html)
    photo_preview.allow_tags = True
    photo_preview.short_description = _("Preview")

    def size(self, obj):
        _size = obj.get_size()
        return "%sx%s" % _size if _size else _("(Blank)")
    size.short_description = _("Size")

    # actions
    def change_watermark(self, request, queryset):
        title = _("Change watermark")
        action = 'change_watermark'
        object_id_set = ','.join([str(obj.id) for obj in queryset])

        extra_context = {
            "title": title,
            "action": action,
            "object_id_set": object_id_set,
            "watermark_tuple": get_watermark_choice(),
        }
        return shortcuts.render(request, 'admin/action_form.html', extra_context)
    change_watermark.short_description = _("Change watermark")

    def change_watermark_action(self, request):
        model = self.queryset(request).model
        object_id_set = request.POST.get('object_id_set')
        watermark = request.POST.get('watermark')
        queryset = model.objects.filter(id__in = object_id_set.split(','))
        for obj in queryset:
            obj.watermark = watermark
            obj.save(update_fields = ['watermark'])
        self.message_user(request, _("Watermark changed successfully"))
