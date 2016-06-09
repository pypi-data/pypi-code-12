# Copyright (c) AppDynamics, Inc., and its affiliates
# 2015
# All Rights Reserved

"""Interceptor for Django.

"""

from appdynamics.agent.interceptor.frameworks.wsgi import WSGIInterceptor
from appdynamics.agent.interceptor.base import BaseInterceptor


class DjangoBaseHandlerInterceptor(BaseInterceptor):
    def _handle_uncaught_exception(self, handle_uncaught_exception, base_handler, request, resolver, exc_info):
        with self.log_exceptions():
            bt = self.bt
            if bt:
                bt.add_exception(*exc_info)

        return handle_uncaught_exception(base_handler, request, resolver, exc_info)


def intercept_django_wsgi_handler(agent, mod):
    WSGIInterceptor(agent, mod.WSGIHandler).attach('__call__')


def intercept_django_base_handler(agent, mod):
    DjangoBaseHandlerInterceptor(agent, mod.BaseHandler).attach('handle_uncaught_exception')
