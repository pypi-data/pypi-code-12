"""User configuration access via the django admin."""

from django.contrib import admin

from .models import DataType, Config


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
    """Django admin for the DataType model."""

    list_display = ('name', 'serializer_class')


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    """Django admin for the Config model."""

    list_display = ('key', 'value', 'default_value', 'data_type', 'allow_template_use', 'in_cache')
    fields = ('key', 'value', 'data_type', 'default_value', 'allow_template_use')
    readonly_fields = ('default_value',)
    list_filter = ('data_type', 'allow_template_use')
