from __future__ import unicode_literals

from django.utils.deconstruct import deconstructible
from django.utils.encoding import force_text
from django.core.validators import EmailValidator
from rest_framework import status

from .status import ApiStatus, EMAIL_ADDRESS_INVALID


@deconstructible
class EmailValidator(EmailValidator):
    def __call__(self, value):
        value = force_text(value)

        if not value or '@' not in value:
            raise Exception(ApiStatus(EMAIL_ADDRESS_INVALID).get_json())

        user_part, domain_part = value.rsplit('@', 1)

        if not self.user_regex.match(user_part):
            raise Exception(ApiStatus(EMAIL_ADDRESS_INVALID).get_json())

        if (domain_part not in self.domain_whitelist and
                not self.validate_domain_part(domain_part)):
            # Try for possible IDN domain-part
            try:
                domain_part = domain_part.encode('idna').decode('ascii')
                if self.validate_domain_part(domain_part):
                    return
            except UnicodeError:
                pass
            raise Exception(ApiStatus(EMAIL_ADDRESS_INVALID).get_json())


validate_email = EmailValidator()
