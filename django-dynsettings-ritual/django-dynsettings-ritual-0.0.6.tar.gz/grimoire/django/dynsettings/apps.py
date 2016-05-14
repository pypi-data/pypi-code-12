from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DefaultAppConfig(AppConfig):
    name = 'grimoire.django.dynsettings'
    verbose_name = _(u'System Dynamic Settings')