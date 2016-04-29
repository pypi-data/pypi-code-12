"""Admin classes for the outlets app."""
from django.contrib import admin

from . import models


class OutletInline(admin.TabularInline):
    """Inline admin for the Outlet model."""
    model = models.Outlet


class OutletAdmin(admin.ModelAdmin):
    """Custom admin for the ``Outlet`` model."""
    list_display = ['name', 'country', 'city', 'street', 'position',
                    'start_date', 'end_date', 'outlet_type', 'lat', 'lon']
    list_filter = ['country__name', 'outlet_type', ]
    search_fields = ['name']


class OutletCountryAdmin(admin.ModelAdmin):
    """Custom admin for the ``OutletCountry`` model."""
    list_display = ['name', 'slug', 'position']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name', )}
    inlines = [OutletInline]


admin.site.register(models.OutletCountry, OutletCountryAdmin)
admin.site.register(models.Outlet, OutletAdmin)
