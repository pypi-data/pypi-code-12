from django import forms
if hasattr(forms, 'Manipulator'):
    try:
        from django import newforms as forms
    except ImportError:
        from django import forms

from mauveinternet.ordering.lockbox import Lockable
from mauveinternet.ordering.models import get_order_model, get_status_options
from mauveinternet.ordering.card import is_valid_pan

class CardNumberField(forms.RegexField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 19
        kwargs['min_length'] = 13
        kwargs['regex'] = '^[0-9 ]*$'
        super(CardNumberField, self).__init__(*args, **kwargs)
        self.error_messages['invalid']=u'Please enter a valid credit card number'

    def clean(self, value):
        card_number=super(CardNumberField, self).clean(value)

        if not is_valid_pan(card_number):
            raise forms.ValidationError(self.error_messages['invalid'])

        return value


class CheckoutForm(forms.ModelForm):
    card_type=forms.ChoiceField(choices=[(c,c) for c in ['Mastercard', 'Visa', 'Maestro', 'Solo']])
    name_on_card=forms.CharField()
    card_number=CardNumberField()

    card_start_date=forms.RegexField(regex=r'^(01|02|03|04|05|06|07|08|09|10|11|12)\s*/\s*([0-9]{4})$', required=False, help_text=u'In MM/YYYY format (Where applicable)')
    card_expiry_date=forms.RegexField(regex=r'^(01|02|03|04|05|06|07|08|09|10|11|12)\s*/\s*([0-9]{4})$', help_text=u'In MM/YYYY format')

    card_issue_number=forms.IntegerField(required=False, help_text=u'For Maestro/Solo cards only')

    card_cv2_number=forms.IntegerField(label=u'CV2 Number', help_text=u'This is the last group of digits on the reverse of the card, usually at the top of the signature strip.', error_messages={'invalid': u'Please enter a numeric value'})

    class Meta:
        model = get_order_model()
        fields=('billing_address', 'billing_postcode')


class AlternatePaymentForm(forms.ModelForm):
    class Meta:
        model = get_order_model()
        fields=('billing_address', 'billing_postcode')


class OrderStatusForm(forms.Form):
    def __init__(self, *args, **kwargs):
        kwargs['auto_id'] = 'st_%s'
        if 'instance' in kwargs:
            instance = kwargs.pop('instance')
            super(OrderStatusForm, self).__init__(*args, **kwargs)
            self.fields['order_status'].default = instance.status
        else:
            super(OrderStatusForm, self).__init__(*args, **kwargs)

    order_status = forms.ChoiceField(choices=[c for c in get_status_options() if c[0] != 'C'])
    message = forms.CharField(max_length=255, initial='Status changed by administrator')


class PassphraseForm(forms.Form):
    def __init__(self, lockable, *args, **kwargs):
        kwargs['auto_id'] = 'pp_%s'
        self.lockable = lockable
        super(PassphraseForm, self).__init__(*args, **kwargs)

    passphrase = forms.CharField(widget=forms.PasswordInput)

    def clean_passphrase(self):
        value=self.cleaned_data['passphrase']
        try:
            self.lockable.unlock(str(value))
        except Lockable.InvalidPassphrase, e:
            raise forms.ValidationError(unicode(e))

        return value
