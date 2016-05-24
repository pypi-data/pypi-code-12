# -*- coding: utf-8 -*-
from django.contrib.admin import SimpleListFilter
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

class SexListFilter(SimpleListFilter):
    title = _("Sex")
    parameter_name = 'sex'

    def lookups(self, request, model_admin):
        return (
            ('m', _("Male")),
            ('f', _("Female")),
            ('n', _("Unknown")),
        )

    def queryset(self, request, queryset):
        if self.value() == 'm':
            return queryset.filter(sex = 'm')
        if self.value() == 'f':
            return queryset.filter(sex = 'f')
        if self.value() == 'n':
            return queryset.filter(Q(sex__isnull = True) | Q(sex = ''))

class VocativeListFilter(SimpleListFilter):
    title = _("Vocative")
    parameter_name = 'vocative'

    def lookups(self, request, model_admin):
        return (
            ('1', _("Yes")),
            ('0', _("No")),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.exclude(Q(vocative__isnull = True) | Q(vocative = ''))
        if self.value() == '0':
            return queryset.filter(Q(vocative__isnull = True) | Q(vocative = ''))
