from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def overridable(name, default=None, required=False):
    if required:
        if not hasattr(settings, name) or not getattr(settings, name):
            raise ImproperlyConfigured("%s must be defined in Django settings" % name)
    return getattr(settings, name, default)


UPS_DEFAULT_SHIP_FROM = overridable('UPS_DEFAULT_SHIP_FROM')
UPS_DEFAULT_SHIP_TO = overridable(
    'UPS_DEFAULT_SHIP_TO',
    default={
        "Address": {
            "CountryCode": "US",
        }
    }
)
UPS_USERNAME = overridable('UPS_USERNAME', required=True)
UPS_PASSWORD = overridable('UPS_PASSWORD', required=True)
UPS_ACCESS_LICENSE_NUMBER = overridable('UPS_ACCESS_LICENSE_NUMBER', required=True)
UPS_BUFFER_DAYS = overridable('UPS_BUFFER_DAYS', default=0)
UPS_DEFAULT_SHIPMENT_WEIGHT = overridable('UPS_DEFAULT_SHIPMENT_WEIGHT')
UPS_DEFAULT_INVOICE = overridable('UPS_DEFAULT_INVOICE')
UPS_TEST_LIVE = overridable('UPS_TEST_LIVE', default=False)
UPS_CACHE_NAME = overridable('UPS_CACHE_NAME', default="default")
