# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

KEY_FIELD_REQUIRED = 300000
EMAIL_ALREADY_REGISTERED = 300001
EMAIL_FIELD_REQUIRED = 300002
VERIFICATION_KEY_INVALID = 300003
VERIFICATION_KEY_VERIFIED = 300004
EMAIL_ADDRESS_DOES_NOT_EXIST = 300005
REFUSED_TO_RESEND_EMAIL = 300006
CONFIRMATION_DOES_NOT_EXIST = 300007
EMAIL_ADDRESS_INVALID = 300008
USER_DOES_NOT_EXIST = 300009
REQUEST_METHOD_NOT_ALLOWED = 300010
PASSWORD_FIELD_REQUIRED = 300011
PASSWORD_CONFIRMATION_FIELD_REQUIRED = 300012
PASSWORD_MISMATCH = 300013
CHANGE_EMAIL_ADDRESS_EXIST = 300014


STATUS_DICT = {
    KEY_FIELD_REQUIRED: _('Must include "key"'),
    EMAIL_ALREADY_REGISTERED: _('A user is already registered with this email address'),
    EMAIL_FIELD_REQUIRED: _('Must include "email"'),
    VERIFICATION_KEY_INVALID: _('Verification key is invalid'),
    VERIFICATION_KEY_VERIFIED: _('Verification key is verified'),
    EMAIL_ADDRESS_DOES_NOT_EXIST: _('Email address does not exist'),
    REFUSED_TO_RESEND_EMAIL: _('Refused to resend email'),
    CONFIRMATION_DOES_NOT_EXIST: _('Confirmation does not exist'),
    EMAIL_ADDRESS_INVALID: _('Email address invalid'),
    USER_DOES_NOT_EXIST: _('User does not exist'),
    REQUEST_METHOD_NOT_ALLOWED: _('Request method not allowed'),
    PASSWORD_FIELD_REQUIRED: _('Must include "new_password1"'),
    PASSWORD_CONFIRMATION_FIELD_REQUIRED: _('Must include "new_password2"'),
    PASSWORD_MISMATCH: _('The two password fields didn\'t match'),
    CHANGE_EMAIL_ADDRESS_EXIST: _('Change email already exists'),
}


class ApiStatus:
    status_code = None
    status_message = None

    def __init__(self, status_code, status_message=None):
        self.status_code = status_code
        self.status_message = status_message

    def get_message(self):
        for key, value in STATUS_DICT.items():
            if key == self.status_code:
                return value
        return None

    def get_json(self):
        if not self.status_message:
            self.status_message = self.get_message()

        return {
            'code': self.status_code,
            'message': self.status_message
        }
