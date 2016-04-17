from django.conf import settings

from appconf import AppConf


class CachedHttpblAppConf(AppConf):

    API_KEY = getattr(settings, 'CACHED_HTTPBL_API_KEY', None)
    API_HOST = getattr(settings, 'CACHED_HTTPBL_API_HOST', 'dnsbl.httpbl.org')
    API_TIMEOUT = getattr(settings, 'CACHED_HTTPBL_API_TIMEOUT', 5)
    HARMLESS_AGE = getattr(settings, 'CACHED_HTTPBL_HARMLESS_AGE', 14)
    THREAT_SCORE = getattr(settings, 'CACHED_HTTPBL_THREAT_SCORE', 5)
    USE_CACHE = getattr(settings, 'CACHED_HTTPBL_USE_CACHE', True)
    CACHE_BACKEND = getattr(settings, 'CACHED_HTTPBL_CACHE_BACKEND', None)
    CACHE_TIMEOUT = getattr(settings, 'CACHED_HTTPBL_CACHE_TIMEOUT', 86400)
    REDIRECT_URL = getattr(settings, 'CACHED_HTTPBL_REDIRECT_URL', None)
    RESPONSE_NOT_FOUND_HTML = getattr(settings, 'CACHED_HTTPBL_RESPONSE_NOT_FOUND_HTML', '<h1>Not Found</h1>')
    IGNORE_REQUEST_METHODS = getattr(settings, 'CACHED_HTTPBL_IGNORE_REQUEST_METHODS', ())
    USE_LOGGING = getattr(settings, 'CACHED_HTTPBL_USE_LOGGING', False)

    class Meta:
        prefix = 'CACHED_HTTPBL'
