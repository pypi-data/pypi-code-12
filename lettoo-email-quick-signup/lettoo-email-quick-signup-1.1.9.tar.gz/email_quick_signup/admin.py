import django
from django.contrib import admin

from .models import QuickEmailConfirmation, QuickEmailAddress
from .adapter import get_adapter


class QuickEmailAddressAdmin(admin.ModelAdmin):
    list_display = ('email', 'user', 'primary', 'verified')
    list_filter = ('primary', 'verified')
    search_fields = []
    raw_id_fields = ('user',)

    def __init__(self, *args, **kwargs):
        super(QuickEmailAddressAdmin, self).__init__(*args, **kwargs)
        if not self.search_fields and django.VERSION[:2] < (1, 7):
            self.search_fields = self.get_search_fields(None)

    def get_search_fields(self, request):
        base_fields = get_adapter().get_user_search_fields()
        return ['email'] + list(map(lambda a: 'user__' + a, base_fields))


class QuickEmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('email_address', 'created', 'sent', 'key')
    list_filter = ('sent',)
    raw_id_fields = ('email_address',)


admin.site.register(QuickEmailConfirmation, QuickEmailConfirmationAdmin)
admin.site.register(QuickEmailAddress, QuickEmailAddressAdmin)
