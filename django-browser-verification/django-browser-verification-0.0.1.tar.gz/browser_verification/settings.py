
from django.conf import settings as django_settings


MIN_BROWSER_VERSIONS = getattr(django_settings, "MIN_BROWSER_VERSIONS", {
    'Chrome': 49.0,
    'Firefox': 45.0,
    'IE': 11.0,
    'Edge': 12,
    'Safari': 8
})
