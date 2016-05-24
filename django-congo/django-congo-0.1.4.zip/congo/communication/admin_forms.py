# -*- coding: utf-8 -*-
from django import forms
import autocomplete_light
from communication.models import EmailRecipient

class EmailRecipientForm(forms.ModelForm):
    class Meta:
        model = EmailRecipient
        widgets = {
            'vocative': autocomplete_light.TextWidget('EmailRecipientVocativeAutocomplete'),
        }
