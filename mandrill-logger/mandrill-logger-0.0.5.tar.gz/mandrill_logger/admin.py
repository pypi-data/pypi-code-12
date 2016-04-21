from django.contrib import admin
from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('email', 'mandrill_id', 'status', 'reason', 'template', 'created_at')
    list_filter = ('status', 'reason', 'template')
    search_fields = ('email', 'mandrill_id', 'template')

admin.site.register(Log, LogAdmin)