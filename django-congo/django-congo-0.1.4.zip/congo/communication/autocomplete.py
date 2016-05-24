# -*- coding: utf-8 -*-
from congo.admin.autocomplete import HtmlAutocomplete
from congo.communication import get_email_recipient_model
from django.db.models import Q
import autocomplete_light.shortcuts as autocomplete_light

class EmailRecipientVocativeAutocomplete(autocomplete_light.AutocompleteChoiceListBase):
    search_fields = ['vocative']
    model = get_email_recipient_model()
    choices = model.objects.exclude(Q(vocative__isnull = True) | Q(vocative = "")).values_list('vocative', 'vocative').order_by('vocative').distinct()

class SMSRecipientAutocomplete(HtmlAutocomplete):
    search_fields = ['name', 'mobile_phone']
