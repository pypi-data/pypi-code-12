# -*- coding: utf-8 -*-
from watson.http.sessions.abc import StorageMixin, COOKIE_KEY
from watson.http.sessions.file import Storage as File
from watson.http.sessions.memory import Storage as Memory
from watson.http.sessions.memcache import Storage as Memcache
from watson.http.sessions.redis import Storage as Redis


__all__ = ('StorageMixin',
           'File',
           'Memory',
           'Memcache',
           'Redis',
           'session_to_cookie')


def session_to_cookie(request, response):
    """Migrate the session id to the cookie.

    Args:
        request (watson.http.messages.Request): The request containing the session
        response (watson.http.messages.Response): The response to be outputed
    """
    if not request.session:
        return
    if not request.session.modified:
        return
    session_cookie = request.cookies[COOKIE_KEY]
    if ((not session_cookie
         or (session_cookie and request.session.id != session_cookie.value))
            and len(request.session) > 0):
        if request.is_secure():
            request.session.cookie_params['secure'] = True
        request.cookies.add(
            COOKIE_KEY,
            value=request.session.id,
            **request.session.cookie_params)
        request.cookies[COOKIE_KEY] = request.session.id
        response.cookies.merge(request.cookies)
