# coding=utf-8

from django.contrib import admin

from . import models


@admin.register(models.Country)
class CountryAdmin(admin.ModelAdmin):

    """Country model admin interface."""

    list_display = ('name', 'vk_id')
    search_fields = ('name',)


@admin.register(models.Region)
class RegionAdmin(admin.ModelAdmin):

    """Region model admin interface."""

    list_display = ('name', 'vk_id', 'country')
    search_fields = ('name',)
    list_filter = ('country',)


@admin.register(models.City)
class CityAdmin(admin.ModelAdmin):

    """City model admin interface."""

    list_display = ('name', 'vk_id', 'area', 'region')
    search_fields = ('name',)
    list_filter = ('region__country', 'region')
