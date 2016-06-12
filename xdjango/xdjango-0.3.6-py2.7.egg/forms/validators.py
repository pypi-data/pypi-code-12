# -*- coding: utf-8 -*-

from django.forms import (Form, CharField, EmailField,)

from xdjango.forms.fields import EmailOrPhoneNumberField, PhoneNumberField
from xdjango.core.validators import is_valid_email, is_valid_phone_number
from xdjango.contrib.captcha import validate_captcha


FIELD_NAME_MAPPING = {
    'g_recaptcha_response': 'g-recaptcha-response',
}


class ReCaptchaFormValidator(Form):
    g_recaptcha_response = CharField()

    def add_prefix(self, field_name):
        # look up field name; return original if not found
        field_name = FIELD_NAME_MAPPING.get(field_name, field_name)
        return super(ReCaptchaFormValidator, self).add_prefix(field_name)

    def clean(self):
        cleaned_data = super(ReCaptchaFormValidator, self).clean()
        g_recaptcha_response = cleaned_data.get("g_recaptcha_response")

        if not validate_captcha(g_recaptcha_response):
            #msg = "Human verification failed."
            msg = u"Falló la verificación anti robots."
            self.add_error('g_recaptcha_response', msg)


class EmailOrPhoneNumberFormValidator(Form):
    """

    """
    email = EmailField(required=False)
    phone_number = PhoneNumberField(required=False)
    email_or_phone_number = EmailOrPhoneNumberField(required=False)
    user_id = CharField(required=False)

    def clean(self):
        cleaned_data = super(EmailOrPhoneNumberFormValidator, self).clean()
        email = cleaned_data.get("email")
        phone_number = cleaned_data.get("phone_number")
        email_or_phone_number = cleaned_data.get("email_or_phone_number")
        user_id = cleaned_data.get("user_id")

        if not self.errors and not email and not phone_number and not email_or_phone_number and not user_id:
            #msg = "Must put 'at least' one of email or phone number."
            msg = u"Debes facilitar, al menos, tu correo electrónico o tu número de teléfono."
            self.add_error('email', msg)
            self.add_error('phone_number', msg)
            self.add_error('email_or_phone_number', msg)

    def clean_email(self):
        cleaned_data = super(EmailOrPhoneNumberFormValidator, self).clean()
        data = cleaned_data.get("email")
        if data:
            return data
        email_or_phone_number = cleaned_data.get("email_or_phone_number")
        if is_valid_email(email_or_phone_number):
            return email_or_phone_number
        return data

    def clean_phone_number(self):
        cleaned_data = super(EmailOrPhoneNumberFormValidator, self).clean()
        data = cleaned_data.get("phone_number")
        if data:
            return data
        email_or_phone_number = cleaned_data.get("email_or_phone_number")
        if is_valid_phone_number(email_or_phone_number):
            return email_or_phone_number
        return data

    def clean_email_or_phone_number(self):
        cleaned_data = super(EmailOrPhoneNumberFormValidator, self).clean()
        data = cleaned_data.get("email_or_phone_number")
        if data:
            return data
        data = cleaned_data.get("email")
        if data:
            return data
        return cleaned_data.get("phone_number")