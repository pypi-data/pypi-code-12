# -*- coding: utf-8 -*-
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

POLISH_PHONE_REGEX = RegexValidator(regex = r'^(\+48|0048)?\d{9}$', message = _("Valid phone number format is '999999999'. 9 digits allowed."))
PHONE_REGEX = RegexValidator(regex = r'^\+?1?\d{9,15}$', message = _("Valid phone number format is '+99999999999'. From 9 up to 15 digits allowed."))
