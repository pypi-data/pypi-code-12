"""Signed Session Cookies for Zope2"""

from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from ZPublisher.interfaces import IPubBeforeCommit
from pyramid.session import BaseCookieSessionFactory
from pyramid.session import SignedCookieSessionFactory
from zope.component import adapter
from zope.component import getUtility
from zope.component import provideHandler
from zope.event import notify
from zope.interface import implementer

from .interfaces import ISignedSessionCookieConfig
from .interfaces import ISignedSessionCookieCreated

ZopeCookieSession = None

def _getSessionClass():
    """Defer initializing session class parameters at import time.

    Wait until ZCA is available.
    """
    global ZopeCookieSession

    if ZopeCookieSession is None:
        config = getUtility(ISignedSessionCookieConfig)
        attrs = config.getCookieAttrs()
        if 'serializer' in attrs:
            PyramidCookieSession = BaseCookieSessionFactory(**attrs)
        else:
            PyramidCookieSession = SignedCookieSessionFactory(**attrs)

        class ZopeCookieSession(PyramidCookieSession):
            """Wrap Pyramid's class, adding Zope2 security majyk.
            """
            security = ClassSecurityInfo()
            security.setDefaultAccess('allow')
            security.declareObjectPublic()

            def __guarded_getitem__(self, key):
                return self[key]

            def __guarded_setitem__(self, key, value):
                self[key] = value

            def __guarded_delitem__(self, key):
                del self[key]

            def set(self, key, value):
                self[key] = value

        InitializeClass(ZopeCookieSession)

    return ZopeCookieSession


@implementer(ISignedSessionCookieCreated)
class SignedSessionCookieCreated(object):
    """Event implementation:  new session created."""
    def __init__(self, session):
        self.session = session


def ssc_hook(container, request):
    """Hook for '__before_traverse__' on root object.

    Establishes 'pyramid.session'-compatible methods on request/response,
    and sets up the wrapper session class.
    """
    # Make the request emulate Pyramid's response.
    request._response_callbacks = []
    def _add_response_callback(func):
        request._response_callbacks.append(func)
    request.add_response_callback = _add_response_callback

    # Make the response emulate Pyramid's response.
    response = request.RESPONSE
    def _setCookie(name, value, quoted=True, **kw):
        scrubbed = dict([(k, v) for k, v in kw.items() if v])
        scrubbed['http_only'] = scrubbed.pop('httponly')
        response.setCookie(name, value, quoted=quoted, **scrubbed)
    response.set_cookie = _setCookie

    # Set up the lazy SESSION implementation.
    klass = _getSessionClass()
    def _with_event():
        session = klass(request)
        if klass._cookie_name not in request.cookies:
            notify(SignedSessionCookieCreated(session))
        return session
    request.set_lazy('SESSION', _with_event)


@adapter(IPubBeforeCommit)
def _emulate_pyramid_response_callback(event):
    request = event.request
    response = request.RESPONSE
    for callback in getattr(request, '_response_callbacks', ()):
        callback(request, response)

provideHandler(_emulate_pyramid_response_callback)
