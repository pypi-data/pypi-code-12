from collections import Mapping
import copy
import functools
import inspect
import logging
import random
import sys
import time
import urlparse

from requests.adapters import BaseAdapter, HTTPAdapter
from requests.exceptions import RequestException

from docido_sdk.crawler import Retry
from docido_sdk.toolbox.date_ext import timestamp_ms
from docido_sdk.toolbox.edsl import kwargsql

MAX_COLLISIONS = 5
DEFAULT_RETRY = 60
LOGGER = logging.getLogger(__name__)


def truncated_exponential_backoff(slot_delay, collision=0, max_collisions=5):
    """Truncated Exponential Backoff
    see https://en.wikipedia.org/wiki/Exponential_backoff
    """
    if collision == max_collisions:
        collision = 0
    slots = random.randint(0, collision)
    return slots * slot_delay


def teb_retry(exc=RequestException,
              when=dict(response__status_code=429),
              delay='response__headers__Retry-After',
              max_collisions=MAX_COLLISIONS,
              default_retry=DEFAULT_RETRY):
    """Decorator catching rate limits exceed events during a crawl task.
    It retries the task later on, following a truncated exponential backoff.
    """
    def wrap(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            attempt = kwargs.pop('teb_retry_attempt', 0)
            try:
                return f(*args, **kwargs)
            except exc as e:
                if kwargsql.and_(e, **when):
                    try:
                        retry_after = kwargsql.get(e, delay)
                    except:
                        retry_after = default_retry
                    else:
                        if retry_after is not None:
                            retry_after = int(retry_after)
                        else:
                            retry_after = default_retry
                    countdown = retry_after + truncated_exponential_backoff(
                        retry_after, attempt % max_collisions)
                    raise Retry(kwargs=dict(attempt=attempt + 1),
                                countdown=countdown)
                else:
                    raise e, None, sys.exc_info()[2] # flake8: noqa.
        return wrapped_f
    return wrap


class RLPersistence(object):
    """Abstract class to handle persistence of a
    :py:class:`RateLimiter` state.
    """
    def __init__(self, key, context, **kwargs):
        """
        :param list key:
          provides list of string used to specify the rate limit
          bucket. for instance:

          >>> [
            'docido',
            '{service}',
            '{http_headers[user-agent]'
          ]
          >>>

        :param dict context:
            provide part of the format required to explicit the key.
            for instance:

            >>> dict(service='twitter')
            >>>
        """
        self.key = key
        self.uri_format = 'rl:' + ':'.join(key)
        self.context = context

    def uri(self, context=None):
        """
        :param dict context:
          keys that were missing in the static context given in
          constructor to resolve the butcket name.
        """
        if context is None:
            context = self.context
        else:
            ctx = copy.deepcopy(self.context)
            ctx.update(context)
            context = ctx
        return self.uri_format.format(**context)

    def _get_value(self, rate_limiter):
        return '{0.window}|{0.count}'.format(rate_limiter)

    def _get_kv(self, key):
        raise NotImplementedError()  # pragma: no cover

    def _set_kv(self, key, value):
        raise NotImplementedError()  # pragma: no cover

    def save(self, rate_limiter, context=None):
        self._set_kv(self.uri(context), self._get_value(rate_limiter))

    def load(self, rate_limiter, context=None):
        persisted_value = self._get_kv(self.uri(context=context))
        if persisted_value is not None:
            window, count = map(long, persisted_value.split('|'))
            rate_limiter.window = window
            rate_limiter.count = count
        return rate_limiter


class IndexAPIRLPersistence(RLPersistence):
    """Persistence layer for a :py:class:`RateLimiter` that
    write and load its status thru the key-value store provided
    by an Index API.
    """
    def __init__(self, key, context, **kwargs):
        """
        :param key:
        """
        super(IndexAPIRLPersistence, self).__init__(key, context)

        class RamKV:
            """Fake IndexAPI KVS"""
            def __init__(self):
                self._kv = dict()

            def get_kv(self, key):
                return self._kv.get(key)

            def set_kv(self, key, value):
                self._kv[key] = value

        self.index = kwargs.get('index', RamKV())

    def _set_kv(self, key, value):
        self.index.set_kv(key, value)

    def _get_kv(self, key):
        return self.index.get_kv(key)


class RateLimiter(object):
    """Handle rate-limits to third-parties service.
    """

    def __init__(self, context, **kwargs):
        """
        :param dict context:
          Uniquely describes the consumed resource.
          Used by the persistence layer to forge the URI
          describing the resource.

        :keyword int window_size_sec:
          Size of a time window in seconds.

        :keyword int calls_per_window:
          Number of authorized calls per time-window.

        :keyword persistence:
          persistence class that may extends :py:class:`RLPersistence`

        :keyword persistence_kwargs:
          keywords arguments given to the persistence layer constructor
        """
        self.__calls_per_window = kwargs['calls_per_window']
        self.__window_size = kwargs['window_size_sec'] * 1e3
        self.window = None
        self.count = 0
        persistence = kwargs.get('persistence')
        if persistence is not None:
            persistence_kwargs = kwargs.get('persistence_kwargs') or {}
            self.persistence = persistence(kwargs['key'], context,
                                           **persistence_kwargs)
        else:
            self.persistence = None

    def __call__(self, units=1, waits=True, context=None):
        """To be called before consuming a resource that is subject to rate-limits.

        :param units:
          Number of units consumed by the API call that is about to be made.

        :param waits:
          If enable, then the member functions explictely calls `time.sleep`
          with the appropriate duration.

        :return:
          duration in seconds to wait for in order to stay under
          the rate limits policy
        :rtype: int
        """
        self._load_state(context)
        state_changed = True
        now = timestamp_ms.now()
        if self.window is None:
            self.window = now
        elif self.window + self.__window_size < now:
            self.window = now
            self.count = 0
        if self.count + units <= self.__calls_per_window:
            self.count += units
            eax = 0
        else:
            eax = (self.window + self.__window_size - now) / 1e3
            state_changed = False
        self._save_state(state_changed, context)
        if waits and eax != 0:
            LOGGER.debug('waiting %ss', eax)
            time.sleep(eax)
        return eax

    def _load_state(self, context):
        if self.persistence is not None:
            self.persistence.load(self, context=context)

    def _save_state(self, state_changed, context):
        if state_changed and self.persistence is not None:
            self.persistence.save(self, context=context)

    @classmethod
    def get_configs(cls):
        """Get rate limiters configuration
        specified at application level

        :rtype: dict of configurations
        """
        import docido_sdk.config
        http_config = docido_sdk.config.get('http') or {}
        session_config = http_config.get('session') or {}
        rate_limits = session_config.get('rate_limit') or {}
        return rate_limits

    @classmethod
    def get_config(cls, service, config=None):
        """Get get configuration of the specified rate limiter

        :param str service:
          rate limiter name

        :param config:
          optional global rate limiters configuration.
          If not specified, then use rate limiters configuration
          specified at application level
        """
        config = config or cls.get_configs()
        return config[service]

    @classmethod
    def get(cls, service, config=None, persistence_kwargs=None, **context):
        """Load a rate-limiter from configuration

        :param str service:
          rate limiter name to retrieve
        :param dict config:
          alternate configuration object to use. If `None`, then use the global
          application configuration
        :context:
          Uniquely describe the consumed resource. Used by the persistence layer
          to forge the URI describing the resource.

        :rtype: :py:class:`RateLimiter` or :py:class:`MultiRateLimiter`
        """
        rl_config = cls.get_config(service, config)
        context.update(service=service)
        if isinstance(rl_config, (dict, Mapping)):
            if persistence_kwargs is not None:
                rl_config.update(persistence_kwargs=persistence_kwargs)
            return RateLimiter(context, **rl_config)
        else:
            def _rl(conf):
                conf.setdefault('persistence_kwargs',
                                persistence_kwargs or {})
                return RateLimiter(context, **conf)
            return MultiRateLimiter(
                [_rl(config) for config in rl_config]
            )


class MultiRateLimiter(object):
    """Wrapper around several instances of :py:class:`RateLimiter`
    """
    def __init__(self, rate_limiters):
        """
        :param list rate_limiters:
          list of :py:class:`RateLimiter`
        """
        self.rate_limiters = rate_limiters

    def __call__(self, waits=True, **kwargs):
        """Please refer to :py:method:`RateLimiter.__call__`
        member function.
        May wait if any of the specified rate-limiters exceeds
        its usage.
        """
        delay = reduce(
            max,
            [rate_limiter(waits=False, **kwargs)
            for rate_limiter in self.rate_limiters]
        )
        if waits:
            LOGGER.debug('rate-limits reached, waiting %ss', delay)
            time.sleep(delay)
        return delay


class RLRequestAdapter(BaseAdapter):
    """requests adapter used to apply rate limits to requests calls
    transparently.

    Rate limit context can be specified both in this class constructor
    but also thru headers and parameters of HTTP calls performed on
    the session where is mount this adapter.

      - HTTP headers will be available under the `http_headers`
        rate-limit key.
      - HTTP parameters will be available under the `http_params`
        rate-limit key. Note that only parameters that appear once
        in URL can be used.
    """
    def __init__(self, *args, **kwargs):
        """
        :keyword py:class:`requests.adapters.BaseAdapter` base_adapter:
          real adapter where requests are forwarded to.
          Can be either an instance of a class.

        Other tuple and keywords arguments are given to the
        :py:class:`RateLimiter` constructor.
        """
        self.base_adapter = kwargs.pop('base_adapter', HTTPAdapter)
        if inspect.isclass(self.base_adapter):
            self.base_adapter = self.base_adapter()
        self.rate_limiter = RateLimiter.get(*args, **kwargs)
        super(RLRequestAdapter, self).__init__()

    def send(self, request, **kwargs):
        context = self._get_context(request)
        while self.rate_limiter(context=context) != 0:
            pass
        return self.base_adapter.send(request, **kwargs)

    def _get_context(cls, prepared_request):
        details = urlparse.urlparse(prepared_request.url)
        params = urlparse.parse_qs(details.query)
        params = dict((k, v[0]) for k, v in params.items() if len(v) == 1)
        return dict(
            http_headers=prepared_request.headers,
            http_params=params
        )

    def close(self, *args, **kwargs):
        return self.base_adapter.close(*args, **kwargs)
