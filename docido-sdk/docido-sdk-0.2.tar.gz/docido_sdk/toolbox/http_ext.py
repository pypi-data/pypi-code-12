from contextlib import contextmanager

import requests
import json

from . rate_limits import (
    RateLimiter,
    RLRequestAdapter,
)


__all__ = [
    'activate_pyopenssl_for_urllib3',
    'HTTP_SESSION',
]
HTTP_SESSION = requests.Session()


def activate_pyopenssl_for_urllib3():
    """
    Workaround issue described here:
    https://urllib3.readthedocs.org/en/latest/security.html#insecureplatformwarning

    """
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()


class delayed_request(object):
    """Build streamed file-like instances from an HTTP request.
    """
    def __init__(self, url, method='GET', **kwargs):
        """
        :param basestring url:
          Resource URL

        :param basestring method:
          HTTP method

        :param dict kwargs:
          Optional parameters given to the `requests.sessions.Session.request`
          member method.
        """
        self.__url = url
        self.__method = method
        self.__kwargs = kwargs.copy()

    @contextmanager
    def open(self, session=None):
        """
        :param requests.Session session:
          Optional requests session


        :return:
          file-like object over the decoded bytes
        """
        self.__kwargs.update(stream=True)
        session = session or requests
        resp = session.request(self.__method, self.__url, **self.__kwargs)
        try:
            yield resp
        finally:
            resp.close()

    def __repr__(self):
        return json.dumps(self.__kwargs)


class HttpSessionPreparer(object):
    """Provides utility class methods to tweak a
    :py:class:`requests.Session`
    """
    @classmethod
    def mount_rate_limit_adapters(cls, session=None,
                                  rls_config=None, **kwargs):
        """Mount rate-limits adapters on the specified `requests.Session`
        object.

        :param py:class:`requests.Session` session:
          Session to mount. If not specified, then use the global
          `HTTP_SESSION`.

        :param dict rls_config:
          Rate-limits configuration. If not specified, then
          use the one defined at application level.

        :param kwargs:
          Additional keywords argument given to
          py:class:`docido_sdk.toolbox.rate_limits.RLRequestAdapter`
          constructor.
        """
        session = session or HTTP_SESSION
        if rls_config is None:
            rls_config = RateLimiter.get_configs()
        for name, rl_conf in rls_config.items():
            urls = rl_conf.get('urls', [])
            if not urls:
                continue
            rl_adapter = RLRequestAdapter(name, config=rls_config, **kwargs)
            for url in urls:
                session.mount(url, rl_adapter)


HttpSessionPreparer.mount_rate_limit_adapters(session=HTTP_SESSION)
