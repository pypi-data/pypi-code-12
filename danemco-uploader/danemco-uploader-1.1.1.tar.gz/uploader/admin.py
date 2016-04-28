import os

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import render_to_response
from django.template import Context, RequestContext, Template

from .models import FileUpload, ImageUpload, ThumbnailSize


class ImageUploadAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'display_image',
    )

    search_fields = (
        'name',
        'image',
    )

    actions = [
        'delete_selected',
    ]

    if 'danemco.gallery' in settings.INSTALLED_APPS:
        actions.append('send_to_gallery')

    def send_to_gallery(self, request, queryset):
        from danemco.gallery.models import Album, Photo

        class GalleryForm(forms.Form):
            album = forms.ModelChoiceField(Album.objects.all(), required=True)

        if 'album' in request.POST:
            form = GalleryForm(request.POST)
            if form.is_valid():
                for obj in queryset.all():
                    album = form.cleaned_data['album']
                    photo, created = Photo.objects.get_or_create(album=album, image=obj.image, defaults={'name': os.path.basename(obj.image.name)})
                messages.add_message(request, messages.INFO, 'Images sent to album "%s"' % (album,))
                return None
        else:
            form = GalleryForm()

        return render_to_response(
            'uploader/send_to_gallery.html',
            locals(),
            context_instance=RequestContext(request)
        )

    def display_image(self, obj):
        return Template(
            '{% load thumbnail %}'
            '<img src="{% thumbnail object.image "30x30" %}" alt>'
        ).render(Context({
            'object': obj,
        }))
    display_image.allow_tags = True
    display_image.admin_order_field = 'image'


class FileUploadAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'file',
    )

    search_fields = (
        'name',
        'file',
    )

admin.site.register(ImageUpload, ImageUploadAdmin)
admin.site.register(FileUpload, FileUploadAdmin)
admin.site.register(ThumbnailSize)
