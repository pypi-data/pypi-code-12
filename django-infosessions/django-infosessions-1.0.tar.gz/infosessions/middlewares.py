# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from django.contrib.auth import logout

from .models import SessionInfo
from .constants import SESSION_PROCESSED

logger = logging.getLogger(__name__)


def is_logged(request):
    return hasattr(request, 'user') and request.user.is_authenticated()


def is_processed(request):
    return SESSION_PROCESSED in request.META


class SessionSyncMiddleware(object):

    @staticmethod
    def process_request(request):
        logger.info('processing request')
        if is_processed(request):
            return
        if is_logged(request):
            if not SessionInfo.exists(request):
                SessionInfo.record(request)
        request.META[SESSION_PROCESSED] = True

    @classmethod
    def process_response(cls, request, response):
        if not is_processed(request):
            cls.process_request(request)
        return response


class SessionSameIP(object):

    @staticmethod
    def process_request(request):
        if not is_processed(request):
            return
        if is_logged(request) and not SessionInfo.is_request_valid(request):
            session_key = request.session.session_key
            logger.warning('logging out user with session key %s; ip changed' % session_key)
            logout(request)
            request.session.delete()
