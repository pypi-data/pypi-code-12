from django.forms import TypedMultipleChoiceField, CharField, Field
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_text, force_text
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import  MultipleHiddenInput, SelectMultiple

from xdjango.core import validators


class TypedMultipleField(TypedMultipleChoiceField):

    def validate(self, value):
        """
        Validates if the input is required.
        """
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')


class EmailOrPhoneNumberField(CharField):

    default_validators = [validators.validate_email_or_phone_number]

    def clean(self, value):
        value = self.to_python(value).strip()
        return super(EmailOrPhoneNumberField, self).clean(value)


class PhoneNumberField(CharField):

    default_validators = [validators.validate_phone_number]

    def clean(self, value):
        value = self.to_python(value).strip()
        return super(PhoneNumberField, self).clean(value)


class MultiCharField(Field):
    hidden_widget = MultipleHiddenInput
    widget = SelectMultiple
    default_error_messages = {
        'invalid_list': _('Enter a list of values.'),
    }

    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            raise ValidationError(self.error_messages['invalid_list'], code='invalid_list')
        return [smart_text(val) for val in value]

    def validate(self, value):
        """
        Validates that the input is a list or tuple.
        """
        if self.required and not value:
            raise ValidationError(self.error_messages['required'], code='required')
        # Validate that each value in the value list is in self.choices.
        for val in value:
            """
            if not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},
                )
            """
            pass

    def has_changed(self, initial, data):
        if initial is None:
            initial = []
        if data is None:
            data = []
        if len(initial) != len(data):
            return True
        initial_set = set(force_text(value) for value in initial)
        data_set = set(force_text(value) for value in data)
        return data_set != initial_set