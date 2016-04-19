# Copyright (c) 2015, DjaoDjin inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Session Store for encrypted cookies.
"""
from importlib import import_module
import logging

from django.conf import settings as django_settings
from django.core.exceptions import PermissionDenied
from django.contrib.sessions.middleware import SessionMiddleware \
    as BaseMiddleware

from . import settings


LOGGER = logging.getLogger(__name__)


class SessionMiddleware(BaseMiddleware):

    def process_request(self, request):
        engine = import_module(django_settings.SESSION_ENGINE)
        session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        request.session = engine.SessionStore(session_key)
        if not session_key:
            found = False
            for path in settings.ALLOWED_NO_SESSION:
                if request.path.startswith(str(path)):
                    found = True
                    break
            if not found:
                LOGGER.debug("%s not found in %s",
                    request.path, settings.ALLOWED_NO_SESSION)
                raise PermissionDenied("No DjaoDjin session key")
        try:
            # trigger ``load()``
            request.session._session #pylint: disable=protected-access
        except PermissionDenied:
            if not settings.BACKUP_SESSION_ENGINE:
                raise
            engine = import_module(settings.BACKUP_SESSION_ENGINE)
            request.session = engine.SessionStore(session_key)
            LOGGER.warning("fallback to %s SessionStore",
                settings.BACKUP_SESSION_ENGINE)
