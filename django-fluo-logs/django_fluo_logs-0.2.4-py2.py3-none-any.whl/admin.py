# -*- coding: utf-8 -*-

# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import, division, print_function, unicode_literals
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.admin import SimpleListFilter
from fluo import admin
from fluo import forms
from .models import Log


class RealmFilter(SimpleListFilter):
    title = _("realm")
    parameter_name = "realm"

    def lookups(self, request, model_admin):
        rows = []
        for row in Log.objects.order_by("realm").distinct().values_list("realm", flat=True):
            rows.append((row, row) if row else ("--unset--", ugettext("Not set")))
        return rows

    def queryset(self, request, queryset):
        realm = self.value()
        if realm == "--unset--":
            return queryset.filter(realm__isnull=True)
        elif realm:
            return queryset.filter(realm__iexact=realm)
        else:
            return queryset


class LogForm(forms.ModelForm):
    pass
class LogAdmin(admin.ModelAdmin):
    form = LogForm
    ordering = ["-timestamp"]
    list_display = ["timestamp", "realm", "level", "_short_message"]
    list_filter = [RealmFilter, "level"]
    search_fields = ["level", "realm", "message"]
    related_search_fields = {
        "user": ("pk", "username", "first_name", "last_name", "email"),
    }
    exclude = ["message"]

    def has_add_permission(self, request):
        return False
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ("user", "content_type", "object_id", "object_repr", "level", "realm", "_message", "timestamp")
    def _short_message(self, obj):
        l = 60
        if len(obj.message) > l:
            msg = "{}...".format(obj.message[:l])
        else:
            msg = obj.message
        return msg
    _short_message.short_description = _("Message")
    def _message(self, obj):
        return mark_safe(obj.message.replace("\n", "<br/>").replace("\r", ""))
    _message.short_description = _("Message")
admin.site.register(Log, LogAdmin)
