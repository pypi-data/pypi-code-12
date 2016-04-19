import django
from django.contrib import admin

from .models import QuickPhoneConfirmation, QuickPhoneNumber
from .adapter import get_adapter


class QuickPhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('phone', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    search_fields = []
    raw_id_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(QuickPhoneNumberAdmin, self).__init__(*args, **kwargs)
        if not self.search_fields and django.VERSION[:2] < (1, 7):
            self.search_fields = self.get_search_fields(None)

    def get_search_fields(self, request):
        base_fields = get_adapter().get_user_search_fields()
        return ['phone'] + list(map(lambda a: 'user__' + a, base_fields))


class QuickPhoneConfirmationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'created', 'sent', 'key')
    list_filter = ('sent',)
    raw_id_fields = ('phone_number',)


admin.site.register(QuickPhoneConfirmation, QuickPhoneConfirmationAdmin)
admin.site.register(QuickPhoneNumber, QuickPhoneNumberAdmin)
