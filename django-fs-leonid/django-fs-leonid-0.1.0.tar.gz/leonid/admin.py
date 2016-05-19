# coding=utf-8

from django.contrib import admin

from . import models as _models


@admin.register(_models.LeonidFile)
class LeonidFileAdmin(admin.ModelAdmin):
    pass
