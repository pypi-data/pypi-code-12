from django.contrib import admin
from .models import TaskQueue


class TaskQueueAdmin(admin.ModelAdmin):
    list_display = ('module', 'function', 'is_periodic', 'scheduled', 'status')


admin.site.register(TaskQueue, TaskQueueAdmin)
