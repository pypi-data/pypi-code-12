from webob.cookies import (
    SignedCookieProfile,
    )

from zope.interface import implementer

from .interfaces import (
    IAuthSourceService,
    )

def SessionAuthSourceInitializer(value_key='sanity.'):
    """ An authentication source that uses the current session """

    value_key = value_key + 'value'

    @implementer(IAuthSourceService)
    class SessionAuthSource(object):
        vary = []

        def __init__(self, context, request):
            self.request = request
            self.session = request.session
            self.cur_val = None

        def get_value(self):
            if self.cur_val is None:
                self.cur_val = self.session.get(value_key, [None, None])

            return self.cur_val

        def headers_remember(self, value):
            if self.cur_val is None:
                self.cur_val = self.session.get(value_key, [None, None])

            self.session[value_key] = value
            return []

        def headers_forget(self):
            if self.cur_val is None:
                self.cur_val = self.session.get(value_key, [None, None])

            if value_key in self.session:
                del self.session[value_key]
            return []

    return SessionAuthSource


def CookieAuthSourceInitializer(
    secret,
    cookie_name='auth',
    secure=False,
    max_age=None,
    httponly=False,
    path="/",
    domains=None,
    debug=False,
    hashalg='sha512',
    ):
    """ An authentication source that uses a unique cookie. """

    @implementer(IAuthSourceService)
    class CookieAuthSource(object):
        vary = ['Cookie']

        def __init__(self, context, request):
            self.domains = domains

            if self.domains is None:
                self.domains = []
                self.domains.append(request.domain)

            self.cookie = SignedCookieProfile(
                secret,
                'authsanity',
                cookie_name,
                secure=secure,
                max_age=max_age,
                httponly=httponly,
                path=path,
                domains=domains,
                hashalg=hashalg,
                )
            # Bind the cookie to the current request
            self.cookie = self.cookie.bind(request)

        def get_value(self):
            val = self.cookie.get_value()

            if val is None:
                return [None, None]

            return val

        def headers_remember(self, value):
            return self.cookie.get_headers(value, domains=self.domains)

        def headers_forget(self):
            return self.cookie.get_headers('', max_age=0)

    return CookieAuthSource
