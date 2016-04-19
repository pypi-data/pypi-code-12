import hashlib
import time

from django.core.cache import cache
from django.core.cache.backends.base import BaseCache

from brake.backends import BaseBackend


CACHE_PREFIX = 'rl:'
IP_PREFIX = 'ip:'
KEY_TEMPLATE = 'func:%s:%s%s:%s%s'
PERIOD_PREFIX = 'period:'


class CacheBackend(BaseBackend):

    def get_ip(self, request):
        """This gets the IP we wish to use for ratelimiting.

        It defaults to 'REMOTE_ADDR'. It's recommended that you override
        this function if you're using loadbalancers or any kind of upstream
        proxy service to route requests to Django.
        """
        return request.META['REMOTE_ADDR']

    def _keys(self, func_name, request, ip=True, field=None, period=None):
        keys = []
        if ip:
            keys.append(KEY_TEMPLATE % (
                func_name, PERIOD_PREFIX, period,
                IP_PREFIX, self.get_ip(request)
            ))

        if field is not None:
            if not isinstance(field, (list, tuple)):
                field = [field]
            for f in field:
                val = getattr(request, request.method).get(f)
                # Convert value to hexdigest as cache backend doesn't allow
                # certain characters
                if val:
                    val = hashlib.sha1(val.encode('utf-8')).hexdigest()
                    keys.append('func:%s:%s%s:field:%s:%s' % (
                        func_name, PERIOD_PREFIX, period, f, val
                    ))

        return [
            CACHE_PREFIX + k for k in keys
        ]

    def count(self, func_name, request, ip=True, field=None, period=60):
        """Increment counters for all relevant cache_keys given a request."""
        counters = dict((key, (1, time.time() + period)) for key in self._keys(
            func_name, request, ip, field, period))
        counters.update(cache.get_many(counters.keys()))
        for key, value in counters.items():
            # Handle old values.
            if isinstance(value, tuple):
                count, expiration = value
            else:
                count = value
                expiration = time.time() + period
            count += 1
            cache.set(key, (count, expiration), timeout=int(expiration - time.time()))

    def limit(self, func_name, request,
            ip=True, field=None, count=5, period=None):
        """Return limit data about any keys relevant for requst."""
        counters = cache.get_many(
            self._keys(func_name, request, ip, field, period)
        )

        limits = []
        for counter in counters:
            ratelimited_by = 'field'
            if ':ip:' in counter:
                ratelimited_by = 'ip'

            current_count = counters[counter]
            if isinstance(current_count, tuple):
                current_count = current_count[0]

            if current_count > count:
                limits.append({
                    'ratelimited_by': ratelimited_by,
                    'period': period,
                    'field': field,
                    'count': current_count,
                    'cache_key': counter,
                    'ip': self.get_ip(request)
                })

        return limits
