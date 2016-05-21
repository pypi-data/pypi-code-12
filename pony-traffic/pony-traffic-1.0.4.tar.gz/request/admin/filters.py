from django.contrib import admin
from django.utils.translation import ugettext_lazy as _


class HttpCodeListFilter(admin.SimpleListFilter):
    title = _("HTTP code")
    parameter_name = "http_code"

    def lookups(self, request, model_admin):
        return (
            ('100', _('Information (100)')),
            ('200', _('Success (200)')),
            ('300', _('Redirection (300)')),
            ('400', _('Client error (400)')),
            ('500', _('Server error (500)')),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            code = int(value)
            queryset = queryset.filter(response__gte=code, response__lt=code+100)
        return queryset
