from django.contrib import admin

from acp_calendar.models import HolidayType, ACPHoliday


class HolidayTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name')

class ACPHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'holiday_type')


admin.site.register(HolidayType, HolidayTypeAdmin)
admin.site.register(ACPHoliday, ACPHolidayAdmin)
