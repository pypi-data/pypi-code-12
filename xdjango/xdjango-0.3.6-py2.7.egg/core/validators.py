# -*- coding: utf-8 -*-

import re

from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text
from django.core.validators import validate_ipv46_address, RegexValidator
from django.utils.translation import ugettext_lazy as _
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


@deconstructible
class EmailOrPhoneNumberValidator(object):
    #message = _('Enter a valid email address or phone number.')
    message = _(u'Introduce un correo electrónico o un número de teléfono válidos.')
    code = 'invalid'
    user_regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)',  # quoted-string
        re.IGNORECASE)
    domain_regex = re.compile(
        # max length for domain name labels is 63 characters per RFC 1034
        r'((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+)(?:[A-Z0-9-]{2,63}(?<!-))$',
        re.IGNORECASE)
    literal_regex = re.compile(
        # literal form, ipv4 or ipv6 address (SMTP 4.1.3)
        r'\[([A-f0-9:\.]+)\]$',
        re.IGNORECASE)
    domain_whitelist = ['localhost']
    phone_number_regex = re.compile(r'^\+?1?\d{9,15}$')

    def __init__(self, message=None, code=None, whitelist=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code
        if whitelist is not None:
            self.domain_whitelist = whitelist

    def __call__(self, value):
        value = force_text(value)

        if self.phone_number_regex.match(value):
            return

        if not value or '@' not in value:
            raise ValidationError(self.message, code=self.code)

        user_part, domain_part = value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            raise ValidationError(self.message, code=self.code)

        if (domain_part not in self.domain_whitelist and
                not self.validate_domain_part(domain_part)):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
                if self.validate_domain_part(domain_part):
                    return
            except UnicodeError:
                pass
            raise ValidationError(self.message, code=self.code)

    def validate_domain_part(self, domain_part):
        if self.domain_regex.match(domain_part):
            return True

        literal_match = self.literal_regex.match(domain_part)
        if literal_match:
            ip_address = literal_match.group(1)
            try:
                validate_ipv46_address(ip_address)
                return True
            except ValidationError:
                pass
        return False

    def __eq__(self, other):
        return (
            isinstance(other, EmailOrPhoneNumberValidator) and
            (self.domain_whitelist == other.domain_whitelist) and
            (self.message == other.message) and
            (self.code == other.code)
        )


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def is_valid_phone_number(phone_number):
    if not phone_number:
        return False
    if EmailOrPhoneNumberValidator.phone_number_regex.match(phone_number):
        return True
    return False

validate_email_or_phone_number = EmailOrPhoneNumberValidator()
#msg = "Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
validate_phone_number = RegexValidator(regex=r'^\+?1?\d{9,15}$', message=u"El número de teléfono debe seguir el formato: '+999999999'. Se permiten hasta 15 dígitos.")