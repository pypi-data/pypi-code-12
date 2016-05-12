# coding: utf-8
from django import forms


class TrimmedCharFormField(forms.CharField):

    """ CharField que dá trim nos valores antes do clean """

    def clean(self, value):
        if value:
            value = value.strip()
        return super(TrimmedCharFormField, self).clean(value)
