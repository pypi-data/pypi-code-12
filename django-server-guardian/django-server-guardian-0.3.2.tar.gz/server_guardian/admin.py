"""Admin classes for the server_guardian app."""
from django.contrib import admin

from . import models


class ServerAdmin(admin.ModelAdmin):
    """Custom admin for the ``Server`` model."""
    list_display = ('name', 'url')
    fields = ('name', 'url', 'token')
    search_fields = ['name']


class ServerLogAdmin(admin.ModelAdmin):
    """Custom admin for the ``ServerLog`` model."""
    list_display = ('server', 'label', 'time_logged', 'status_code')
    search_fields = ['response_body', 'content', 'server__name']


admin.site.register(models.Server, ServerAdmin)
admin.site.register(models.ServerLog, ServerLogAdmin)
