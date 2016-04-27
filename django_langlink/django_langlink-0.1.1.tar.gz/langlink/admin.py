from django.contrib import admin


def deactivate(modeladmin, request, queryset):
    queryset.update(active=False)
deactivate.short_description = "Deactivate"


def activate(modeladmin, request, queryset):
    queryset.update(active=True)
activate.short_description = "Activate"


class LanguageAdmin(admin.ModelAdmin):
    list_display = ['title', 'code', 'active']
    actions = [activate, deactivate]

    class Meta:
        abstract = True
