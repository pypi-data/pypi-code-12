import socket
import logging

from django.core import cache
from django.core.exceptions import ImproperlyConfigured

from ipware.utils import is_valid_ipv4

from cached_httpbl.conf import settings

HTTPBL_THREAT_SEARCHENGINE = 0
HTTPBL_THREAT_SUSPICIOUS = 1
HTTPBL_THREAT_HARVESTER = 2
HTTPBL_THREAT_SPAMMER = 4

if settings.CACHED_HTTPBL_USE_LOGGING:
    logger = logging.getLogger(__name__)


class CachedHTTPBL(object):
    def __init__(self, **kwargs):
        """
        Instantiate the CachedHTTPBL object.

        :param kwargs: optional parameters
        :return:
        """

        api_key = kwargs.get('api_key', None)
        api_host = kwargs.get('api_host', None)
        api_timeout = kwargs.get('api_timeout', None)
        use_cache = kwargs.get('use_cache', None)
        cache_backend = kwargs.get('cache_backend', None)
        cache_timeout = kwargs.get('cache_timeout', None)

        # per instance cache
        no_api_key = True
        if hasattr(settings, 'CACHED_HTTPBL_API_KEY'):
            self._api_key = api_key if api_key else settings.CACHED_HTTPBL_API_KEY
            if self._api_key is not None:
                no_api_key = False
        if no_api_key:
            raise ImproperlyConfigured(
                'You should add httpBL API key to your settings. '
                'Please register on http://projecthoneypot.org to get one.'
            )
        self._last_result = None
        self._api_host = api_host if api_host else settings.CACHED_HTTPBL_API_HOST
        self._api_timeout = api_timeout if api_timeout else settings.CACHED_HTTPBL_API_TIMEOUT
        self._use_cache = use_cache if use_cache else settings.CACHED_HTTPBL_USE_CACHE
        self._cache_backend = cache_backend if cache_backend else settings.CACHED_HTTPBL_CACHE_BACKEND
        self._cache_timeout = cache_timeout if cache_timeout else settings.CACHED_HTTPBL_CACHE_TIMEOUT
        self._cache_version = 1

        if self._use_cache and self._cache_backend is None:
            self._cache_backend = 'default'

        if self._use_cache:
            try:
                self._cache = cache.caches[self._cache_backend]
                try:
                    self._cache_version = int(self._cache.get('cached_httpbl_{0}_version'.format(self._api_key)))
                except TypeError:
                    self._cache.set('cached_httpbl_{0}_version'.format(self._api_key), str(1))
            except cache.InvalidCacheBackendError:
                raise ImproperlyConfigured('You should provide valid cache backend!')

    def _make_cache_key(self, ip):
        return 'cached_httpbl_{0}_ip:{1}'.format(self._api_key, ip)

    def _request_httpbl(self, ip):
        query = '.'.join([self._api_key] + ip.split('.')[::-1] + [self._api_host])

        try:
            try:
                socket.setdefaulttimeout(self._api_timeout)
                response = socket.gethostbyname(query)
            except socket.gaierror:
                # error is raised for good ip
                return 0, 0, 0, 0
        except socket.timeout:
            return -1, -1, -1, -1

        error, age, threat, type = [int(x) for x in response.split('.')]

        return error, age, threat, type

    def check_ip(self, ip):
        """
        Check IP trough the httpBL API

        :param ip: ipv4 ip address
        :return: httpBL results or None if any error is occurred
        """

        self._last_result = None

        if is_valid_ipv4(ip):
            key = None
            if self._use_cache:
                key = self._make_cache_key(ip)
                self._last_result = self._cache.get(key, version=self._cache_version)

            if self._last_result is None:
                # request httpBL API
                error, age, threat, type = self._request_httpbl(ip)
                if error == 127 or error == 0:
                    self._last_result = {
                        'error': error,
                        'age': age,
                        'threat': threat,
                        'type': type
                    }
                    if self._use_cache:
                        self._cache.set(key, self._last_result, timeout=self._api_timeout, version=self._cache_version)
            if self._last_result is not None and settings.CACHED_HTTPBL_USE_LOGGING:
                logger.info(
                    'httpBL check ip: {0}; '
                    'httpBL result: error: {1}, age: {2}, threat: {3}, type: {4}'.format(ip,
                                                                                         self._last_result['error'],
                                                                                         self._last_result['age'],
                                                                                         self._last_result['threat'],
                                                                                         self._last_result['type']
                                                                                         )
                )

        return self._last_result

    def is_threat(self, result=None, harmless_age=None, threat_score=None, threat_type=None):
        """
        Check if IP is a threat

        :param result: httpBL results; if None, then results from last check_ip() used (optional)
        :param harmless_age: harmless age for check if httpBL age is older (optional)
        :param threat_score: threat score for check if httpBL threat is lower (optional)
        :param threat_type:  threat type, if not equal httpBL score type, then return False (optional)
        :return: True or False
        """

        harmless_age = harmless_age if harmless_age is not None else settings.CACHED_HTTPBL_HARMLESS_AGE
        threat_score = threat_score if threat_score is not None else settings.CACHED_HTTPBL_THREAT_SCORE
        threat_type = threat_type if threat_type is not None else -1
        result = result if result is not None else self._last_result
        threat = False
        if result is not None:
            if result['age'] < harmless_age and result['threat'] > threat_score:
                threat = True
            if threat_type > -1:
                if result['type'] & threat_type:
                    threat = True
                else:
                    threat = False
        return threat

    def is_suspicious(self, result=None):
        """
        Check if IP is suspicious

        :param result: httpBL results; if None, then results from last check_ip() used (optional)
        :return: True or False
        """

        result = result if result is not None else self._last_result
        suspicious = False
        if result is not None:
            suspicious = True if result['type'] > 0 else False
        return suspicious

    def invalidate_ip(self, ip):
        """
        Invalidate httpBL cache for IP address

        :param ip: ipv4 IP address
        """

        if self._use_cache:
            key = self._make_cache_key(ip)
            self._cache.delete(key, version=self._cache_version)

    def invalidate_cache(self):
        """
        Invalidate httpBL cache
        """

        if self._use_cache:
            self._cache_version += 1
            self._cache.increment('cached_httpbl_{0}_version'.format(self._api_key))
