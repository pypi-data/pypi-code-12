# coding=utf-8
from __future__ import unicode_literals

import re

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.template.loader import (TemplateDoesNotExist, get_template,
                                    select_template)
from django.utils.lru_cache import lru_cache
from django.utils.translation import ugettext_lazy as _


@lru_cache()
def validate_and_get_template(name, using=None):
    if isinstance(name, (list, tuple)):
        return select_template(name, using=using)
    try:
        if not name.endswith('.html'):
            name = '{}.html'.format(name)
        return get_template(name, using=using)
    except TemplateDoesNotExist as e:
        raise ValidationError(_("Unable to find the template '{}'".format(e)))


url_path_re = re.compile(r'^/(?:[-a-zA-Z0-9_]+/{})*$'.format(r'?' if not settings.APPEND_SLASH else r''))
validate_url_path = RegexValidator(
    url_path_re,
    _("Enter a valid 'url path'. Path should start and end with '/'."),
    'invalid'
)
