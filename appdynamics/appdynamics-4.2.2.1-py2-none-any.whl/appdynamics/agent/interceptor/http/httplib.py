# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for httplib.

"""

from . import HTTPConnectionInterceptor


class HttplibConnectionInterceptor(HTTPConnectionInterceptor):
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
            with self.end_exit_call_and_reraise_on_exception(ignored_exceptions=(TypeError,)):
                response = getresponse(connection, *args, **kwargs)
        except TypeError:
            with self.end_exit_call_and_reraise_on_exception():
                response = getresponse(connection)

        self.end_exit_call()
        return response


def intercept_httplib(agent, mod):
    HTTPConnectionInterceptor.https_connection_classes.add(mod.HTTPSConnection)
    interceptor = HttplibConnectionInterceptor(agent, mod.HTTPConnection)
    interceptor.attach(['putrequest', 'endheaders'])
    interceptor.attach('getresponse', wrapper_func=None)   # CORE-40945 Do not wrap getresponse in the default wrapper.
