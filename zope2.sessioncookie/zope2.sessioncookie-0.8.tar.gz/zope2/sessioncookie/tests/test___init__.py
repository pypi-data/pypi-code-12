import unittest


class _Base(unittest.TestCase):

    def setUp(self):
        from zope.component.testing import setUp
        from zope2 import sessioncookie
        setUp()
        sessioncookie.ZopeCookieSession = None

    def tearDown(self):
        from zope.component.testing import tearDown
        from zope2 import sessioncookie
        sessioncookie.ZopeCookieSession = None
        tearDown()

    def _setUpUtility(self, secret='SEEKRIT', cookie_name='COOKIE'):
        from zope.component import provideUtility
        from ..config import SignedSessionCookieConfig
        config = SignedSessionCookieConfig(secret, cookie_name=cookie_name)
        provideUtility(config)


class Test__getSessionClass(_Base):

    def _callFUT(self):
        from .. import _getSessionClass
        return _getSessionClass()

    def test_w_existing_set(self):
        from zope2 import sessioncookie
        EXISTING = sessioncookie.ZopeCookieSession = object()
        klass = self._callFUT()
        self.assertTrue(klass is EXISTING)

    def test_wo_existing_set(self):
        from zope2 import sessioncookie
        self.assertTrue(sessioncookie.ZopeCookieSession is None)
        self._setUpUtility()
        klass = self._callFUT()
        self.assertEqual(klass._cookie_name, 'COOKIE')
        self.assertTrue(sessioncookie.ZopeCookieSession is klass)

    def test_session_class_extras(self):
        self._setUpUtility()
        klass = self._callFUT()
        request = _Request()
        response = request.RESPONSE = _Response()
        session = klass(request)

        session['foo'] = 'bar'
        self.assertEqual(session.__guarded_getitem__('foo'), 'bar')

        session.__guarded_setitem__('foo', 'baz')
        self.assertEqual(session['foo'], 'baz')

        session.__guarded_delitem__('foo')
        self.assertEqual(dict(session), {})

        self.assertEqual(response.counter, 0)  # cookie not set
        self.assertEqual(len(request._response_callbacks), 1)
        request._response_callbacks[0](request, response)
        self.assertEqual(response.counter, 1)

    def test_session_class_set_method(self):
        self._setUpUtility()
        klass = self._callFUT()
        request = _Request()
        session = klass(request)
        session.set('foo', 'bar')
        self.assertEqual(session.__guarded_getitem__('foo'), 'bar')


class SignedSessionCookieCreatedTests(unittest.TestCase):

    _dummy = object()

    def _getTargetClass(self):
        from .. import SignedSessionCookieCreated
        return SignedSessionCookieCreated

    def _makeOne(self, session=_dummy):
        return self._getTargetClass()(session)

    def test_class_conforms_to_ISignedSessionCookieCreated(self):
        from zope.interface.verify import verifyClass
        from ..interfaces import ISignedSessionCookieCreated
        verifyClass(ISignedSessionCookieCreated, self._getTargetClass())

    def test_instance_conforms_to_ISignedSessionCookieCreated(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import ISignedSessionCookieCreated
        verifyObject(ISignedSessionCookieCreated, self._makeOne())


class Test_ssc_hook(_Base):

    def _callFUT(self, container, request):
        from .. import ssc_hook
        return ssc_hook(container, request)

    def setUp(self):
        from zope.event import subscribers
        super(Test_ssc_hook, self).setUp()
        self._old_subscribers = subscribers[:]

    def tearDown(self):
        from zope.event import subscribers
        super(Test_ssc_hook, self).setUp()
        subscribers[:] = self._old_subscribers

    def test_wo_existing_session(self):
        from zope.event import subscribers
        _handled = []
        subscribers.append(_handled.append)

        container = object()
        request = _Request()
        response = request.RESPONSE = _ZopeResponse()
        self._setUpUtility()

        self._callFUT(container, request)

        self.assertTrue(response.set_cookie is not response.setCookie.im_func)
        self.assertEqual(request._lazy.keys(), ['SESSION'])
        self.assertEqual(len(_handled), 0)
        session = request._lazy['SESSION']()
        self.assertEqual(len(_handled), 1)
        event = _handled[0]
        self.assertTrue(event.session is session)

        session['foo'] = 'bar'
        self.assertEqual(response.cookies.keys(), [])

        session['baz'] = 'bam'
        self.assertEqual(response.cookies.keys(), [])

        self.assertEqual(response.counter, 0)  # cookie not set
        self.assertEqual(len(request._response_callbacks), 1)
        request._response_callbacks[0](request, response)
        self.assertEqual(response.counter, 1)
        self.assertEqual(response.cookies.keys(), ['COOKIE'])

        del _handled[:]
        new_request = _Request()
        new_request.cookies['COOKIE'] = response.cookies['COOKIE']
        new_response = new_request.RESPONSE = _ZopeResponse()

        self._callFUT(container, new_request)

        self.assertEqual(len(_handled), 0)
        session = new_request._lazy['SESSION']()
        self.assertEqual(len(_handled), 0)


class Test__emulate_pyramid_response_callback(_Base):

    def _callFUT(self, event):
        from .. import _emulate_pyramid_response_callback
        return _emulate_pyramid_response_callback(event)

    def test_wo_callbacks(self):
        event = _Event()
        self._callFUT(event)  # no exception for missing _response_callbacks

    def test_w_callbacks(self):
        event = _Event()
        _called = []
        def _callback(request, response):
            _called.append((request, response))
        event.request._response_callbacks = [_callback]
        self._callFUT(event)  # no exception for missing _response_callbacks
        self.assertEqual(_called, [(event.request, event.request.RESPONSE)])


class _Response(object):

    counter = 0

    def __init__(self):
        self.cookies = {}

    def set_cookie(self, name, **kw):
        self.cookies[name] = kw
        self.counter += 1


class _ZopeResponse(object):

    counter = 0

    def __init__(self):
        self.cookies = {}

    def setCookie(self, name, value, quoted=True, **kw):
        cookie = kw.copy()
        cookie['value'] = value
        cookie['quoted'] = quoted
        self.cookies[name] = cookie
        self.counter += 1


class _Request(object):

    def __init__(self, **kw):
        self.cookies = kw
        self._lazy = {}

    def set_lazy(self, name, factory):
        self._lazy[name] = factory

    def add_response_callback(self, callback):
        callbacks = getattr(self, '_response_callbacks', None)
        if callbacks is None:
            callbacks = self._response_callbacks = []
        callbacks.append(callback)


class _Event(object):
    def __init__(self):
        request = self.request = _Request()
        response = request.RESPONSE = _Response()
