from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import EmailRegistration, SMSRegistration
from .settings import *


class RegistrationAdmin(admin.ModelAdmin):
    actions = ['verify_users', 'resend_verification_message']
    list_display = ('user', 'expired')
    raw_id_fields = ['user']

    def verify_users(self, request, queryset):
        for registration in queryset:
            EmailRegistration.objects.verify(registration.verification_code)
    verify_users.short_description = _("Verify users")

    def resend_verification_message(self, request, queryset):

        for registration in queryset:
            if not registration.expired():
                registration.send_message()


class EmailRegistrationAdmin(RegistrationAdmin):
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def resend_verification_message(self, request, queryset):
        super(EmailRegistrationAdmin, self).resend_verification_message(request, queryset)
    resend_verification_message.short_description = _("Re-send verification emails")

admin.site.register(EmailRegistration, EmailRegistrationAdmin)

if SMS_ENABLED:
    class SMSRegistrationAdmin(RegistrationAdmin):
        search_fields = ('user__phone', 'user__first_name', 'user__last_name')

        def resend_verification_message(self, request, queryset):
            super(SMSRegistrationAdmin, self).resend_verification_message(request, queryset)
        resend_verification_message.short_description = _("Re-send verification SMS")

    admin.site.register(SMSRegistration, SMSRegistrationAdmin)
