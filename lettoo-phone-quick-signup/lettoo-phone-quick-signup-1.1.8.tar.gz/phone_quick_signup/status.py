# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

KEY_FIELD_REQUIRED = 200000
PHONE_ALREADY_REGISTERED = 200001
PHONE_FIELD_REQUIRED = 200002
VERIFICATION_KEY_INVALID = 200003
VERIFICATION_KEY_VERIFIED = 200004
PHONE_NUMBER_DOES_NOT_EXIST = 200005
REFUSED_TO_RESEND_SMS = 200006
CONFIRMATION_DOES_NOT_EXIST = 200007
PHONE_NUMBER_INVALID = 200008
USER_DOES_NOT_EXIST = 200009
REQUEST_METHOD_NOT_ALLOWED = 200010
PASSWORD_FIELD_REQUIRED = 200011
PASSWORD_CONFIRMATION_FIELD_REQUIRED = 200012
PASSWORD_MISMATCH = 200013
CHANGE_PHONE_NUMBER_EXIST = 200014


STATUS_DICT = {
    KEY_FIELD_REQUIRED: _('Must include "key"'),
    PHONE_ALREADY_REGISTERED: _('A user is already registered with this phone number'),
    PHONE_FIELD_REQUIRED: _('Must include "phone"'),
    VERIFICATION_KEY_INVALID: _('Verification key is invalid'),
    VERIFICATION_KEY_VERIFIED: _('Verification key is verified'),
    PHONE_NUMBER_DOES_NOT_EXIST: _('Phone number does not exist'),
    REFUSED_TO_RESEND_SMS: _('Refused to resend sms'),
    CONFIRMATION_DOES_NOT_EXIST: _('Confirmation does not exist'),
    PHONE_NUMBER_INVALID: _('Invalid phone number'),
    USER_DOES_NOT_EXIST: _('User does not exist'),
    REQUEST_METHOD_NOT_ALLOWED: _('Request method not allowed'),
    PASSWORD_FIELD_REQUIRED: _('Must include "new_password1"'),
    PASSWORD_CONFIRMATION_FIELD_REQUIRED: _('Must include "new_password2"'),
    PASSWORD_MISMATCH: _('The two password fields didn\'t match'),
    CHANGE_PHONE_NUMBER_EXIST: _('Change phone number already exists'),
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
