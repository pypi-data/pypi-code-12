from django.apps import AppConfig as DjangoAppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(DjangoAppConfig):
    """Configuration for the httpBL app (only for Django v1.7+)"""
    label = name = 'cached_httpbl'
    verbose_name = _('Cached httpBL')
