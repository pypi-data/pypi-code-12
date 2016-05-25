# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptors for httplib, urllib, urllib2, urllib3 and requests.

"""

from appdynamics.agent.interceptor.base import ExitCallInterceptor
from appdynamics.agent.models.exitcalls import EXIT_HTTP
from appdynamics.lib import parse_url


class HTTPConnectionInterceptor(ExitCallInterceptor):
    """Base class for http interceptors.

    """

    https_base_classes = set()
    backend_name_format_string = '%s://{HOST}:{PORT}{URL}?{QUERY STRING}'

    def _request_is_https(self, connection):
        if connection.port == 443:
            return True
        return connection.__class__ in self.https_base_classes

    def get_backend(self, host, port, scheme, url):
        parsed_url = parse_url(url)
        backend_properties = {
            'HOST': host,
            'PORT': str(port),
            'URL': parsed_url.path,
            'QUERY STRING': parsed_url.query,
        }
        return self.agent.backend_registry.get_backend(EXIT_HTTP, backend_properties,
                                                       self.backend_name_format_string % scheme)

    def _putrequest(self, putrequest, connection, method, url, *args, **kwargs):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                scheme = 'https' if self._request_is_https(connection) else 'http'
                backend = self.get_backend(connection.host, connection.port, scheme, url)
                if backend:
                    self.start_exit_call(bt, backend, operation=url)
        return putrequest(connection, method, url, *args, **kwargs)

    def _endheaders(self, endheaders, connection, *args, **kwargs):
        with self.log_exceptions():
            header = self.make_correlation_header()
            connection.putheader(*header)
            self.agent.logger.debug('Added correlation header to HTTP request: %s, %s' % header)
        return endheaders(connection, *args, **kwargs)

    def _getresponse(self, getresponse, connection, *args, **kwargs):
        # CORE-40945 Catch TypeError as a special case for Python 2.6 and call getresponse with just the
        # HTTPConnection instance.
        try:
            with self.call_and_reraise_on_exception(self.end_exit_call, ignored_exceptions=(TypeError,)):
                response = getresponse(connection, *args, **kwargs)
        except TypeError:
            with self.call_and_reraise_on_exception(self.end_exit_call):
                response = getresponse(connection)

        self.end_exit_call()
        return response


def intercept_httplib(agent, mod):
    interceptor = HTTPConnectionInterceptor(agent, mod.HTTPConnection)
    interceptor.attach(['putrequest', 'endheaders'])

    # CORE-40945 Do not wrap getresponse in the default wrapper.
    interceptor.attach('getresponse', wrapper_func=None)
    HTTPConnectionInterceptor.https_base_classes.add(mod.HTTPSConnection)


def intercept_urllib3(agent, mod):
    # urllib3 1.8+ provides its own HTTPSConnection class, so we need to add it to our list of base classes.
    if hasattr(mod, 'connection'):
        HTTPConnectionInterceptor.https_base_classes.add(mod.connection.HTTPSConnection)


def intercept_requests(agent, mod):
    # requests ships with its own version of urllib3, so we need to manually intercept it.
    intercept_urllib3(agent, mod.packages.urllib3)


def intercept_boto(agent, mod):
    HTTPConnectionInterceptor.https_base_classes.add(mod.CertValidatingHTTPSConnection)
