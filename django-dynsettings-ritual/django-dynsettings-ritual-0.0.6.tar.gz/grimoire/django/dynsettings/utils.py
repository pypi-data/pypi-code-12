from django.conf import settings as django_settings
from django.core.exceptions import ObjectDoesNotExist
from .models import DynamicSetting


class Settings(object):

    def __getattr__(self, item):
        try:
            return DynamicSetting.objects.get(name=item).value
        except ObjectDoesNotExist:
            return getattr(django_settings, item)


settings = Settings()