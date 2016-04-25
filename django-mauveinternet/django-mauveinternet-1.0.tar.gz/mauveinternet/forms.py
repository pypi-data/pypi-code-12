"""A collection of shortcuts for Django forms that aim to solve some of the problems I
routinely face when programming with forms.

The objective is to create a compatible package by replacing and subclassing, to
make it possible to replace

from django import forms

with

from mauveinternet import forms
"""
import re
from datetime import timedelta

from django.forms import *

DjangoForm = Form

class Form(DjangoForm):
    def add_error(self, message):
        """Add an error to the form corresponding to no one field in particular."""
        from django.forms.forms import NON_FIELD_ERRORS
        self._errors.setdefault(NON_FIELD_ERRORS, self.error_class([])).append(message)

    def add_field_error(self, field, message):
        """Add an error to the form corresponding to a field."""
        self._errors.setdefault(field, self.error_class([])).append(message)

    def value(self, k):
        """Returns cleaned value or None if not provided or not valid."""
        return self.cleaned_data.get(k)

    def value_entered(self, k):
        """Determine if a value was originally supplied for an optional field, irrespective of whether that value was valid.

        For fields that have been validated as required this method will always answer True."""
        from django.forms.fields import EMPTY_VALUES
        return self.cleaned_data.get(k, 'x') not in EMPTY_VALUES

    def ignore(self, k):
        """Deletes the value and any errors associated with field k"""
        self.cleaned_data[k] = None
        if k in self._errors:
            del(self._errors[k])

    def require(self, k):
        """Re-run the 'required' validation. If no value was given, issues the field's 'required'
        message and delete the field from the cleaned_data.

        This allows for conditionally required fields to be implemented via the form's clean() method.
        """
        if not self.value_entered(k):
            self.add_field_error(k, self.fields[k].error_messages['required'])
            if k in self.cleaned_data:
                del(self.cleaned_data[k])
            return False
        return True


class TimeDeltaField(RegexField):
    """A time field that works around the fact that Python times only represent
    a one-day range by representing times as (hour, minute) pairs.

    We could use timedeltas but seconds are very fiddly for many user-facing
    applications; converting to timedeltas is not hard.

    timedeltas can be used for the initial keyword argument, however."""

    TIME_REGEX=r'([0-9]+):([0-9]{2})'
    def __init__(self, *args, **kwargs):
        ka = {'regex': self.TIME_REGEX, 'initial': ':00'}
        ka.update(kwargs)

        initial = ka['initial']
        if isinstance(initial, timedelta):
            hours = initial.days * 24 + initial.seconds//3600
            minutes = ((initial.seconds % 3600) + 30) // 60
            if minutes > 59:
                hours = hours + 1
                minutes = 0
            ka['initial'] = '%d:%02d'%(hours, minutes)

        super(TimeField, self).__init__(*args, **ka)

    def clean(self, value):
        time = value
        mo = re.match(self.TIME_REGEX, time)
        if not mo:
            raise forms.ValidationError('Please enter a time in H:MM format')
        hour = int(mo.group(1))
        minute = int(mo.group(2))

        hour = hour + minute//60
        minute = minute % 60
        return hour, minute
