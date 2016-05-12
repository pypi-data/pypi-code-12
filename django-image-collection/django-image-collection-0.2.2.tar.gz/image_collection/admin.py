"""Admin classes for the image_collection app."""
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from generic_positions.admin import GenericPositionsAdmin

from . import models


class ImageInline(admin.TabularInline):
    model = models.ImageSlide


class ImageCollectionAdmin(admin.ModelAdmin):
    """Custom admin for the ``ImageCollection`` model."""
    list_display = ('identifier', 'name')
    inlines = [ImageInline]


class ImageSlideAdmin(GenericPositionsAdmin):
    """Custom admin for the ``ImageSlide`` model."""
    change_list_template = 'image_collection/admin/change_list.html'
    list_display = (
        'collection', 'get_headline', 'get_caption', 'image', 'image_mobile')
    list_filter = ['collection']

    def get_caption(self, obj):
        return obj.caption
    get_caption.short_description = _('description')

    def get_headline(self, obj):
        return obj.caption_headline
    get_headline.short_description = _('headline')


admin.site.register(models.ImageSlide, ImageSlideAdmin)
admin.site.register(models.ImageCollection, ImageCollectionAdmin)
