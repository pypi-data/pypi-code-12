import unittest


class Test__doConfigure(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from ..zcml import _doConfigure
        return _doConfigure(*args, **kw)

    def test_it(self):
        from zope.component import getUtility
        from ..config import SignedSessionCookieConfig
        from ..interfaces import ISignedSessionCookieConfig
        self._callFUT('SECRET', 'SALT', 'COOKIE', 1234,
                      '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, True)
        config = getUtility(ISignedSessionCookieConfig)
        self.assertTrue(isinstance(config, SignedSessionCookieConfig))
        self.assertEqual(config.secret, 'SECRET')
        self.assertEqual(config.salt, 'SALT')
        self.assertEqual(config.cookie_name, 'COOKIE')
        self.assertEqual(config.max_age, 1234)
        self.assertEqual(config.path, '/foo')
        self.assertEqual(config.domain, 'www.example.com')
        self.assertEqual(config.secure, False)
        self.assertEqual(config.http_only, False)
        # This value is only curried, not stored on the instance.
        #self.assertEqual(config.hashalg, 'md5')
        self.assertEqual(config.timeout, 2345)
        self.assertEqual(config.reissue_time, 234)
        self.assertEqual(config.encrypt, True)


class Test_configureSessionCookie(unittest.TestCase):

    def _callFUT(self, *args, **kw):
        from ..zcml import configureSessionCookie
        return configureSessionCookie(*args, **kw)

    def test_wo_encryt(self):
        from ..zcml import _doConfigure
        context = _Context()
        self._callFUT(context, 'SECRET', 'SALT', 'COOKIE', 1234,
                      '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, False)
        self.assertEqual(len(context.actions), 1)
        args, kw = context.actions[0]
        self.assertEqual(args, ())
        self.assertEqual(kw, {
            'callable': _doConfigure,
            'discriminator': 'configureSessionCookie',
            'args': ('SECRET', 'SALT', 'COOKIE', 1234,
                     '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, False),
        })

    def test_w_encryt_w_secret_not_32_bytes(self):
        context = _Context()
        self.assertRaises(ValueError, self._callFUT,
            context, 'SECRET', 'SALT', 'COOKIE', 1234,
            '/foo', 'www.example.com', False, False,
            'md5', 2345, 234, True)

    def test_w_encryt_w_secret_32_bytes(self):
        from ..zcml import _doConfigure
        context = _Context()
        SECRET = b'\x01' * 32
        self._callFUT(context, SECRET, 'SALT', 'COOKIE', 1234,
                      '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, True)
        self.assertEqual(len(context.actions), 1)
        args, kw = context.actions[0]
        self.assertEqual(args, ())
        self.assertEqual(kw, {
            'callable': _doConfigure,
            'discriminator': 'configureSessionCookie',
            'args': (SECRET, 'SALT', 'COOKIE', 1234,
                     '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, True),
        })

    def test_w_encryt_w_secret_32_bytes_hexlified(self):
        import binascii
        from ..zcml import _doConfigure
        context = _Context()
        SECRET = b'\x01' * 32
        HEXLIFIED = binascii.hexlify(SECRET)
        self._callFUT(context, HEXLIFIED, 'SALT', 'COOKIE', 1234,
                      '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, True)
        self.assertEqual(len(context.actions), 1)
        args, kw = context.actions[0]
        self.assertEqual(args, ())
        self.assertEqual(kw, {
            'callable': _doConfigure,
            'discriminator': 'configureSessionCookie',
            'args': (SECRET, 'SALT', 'COOKIE', 1234,
                     '/foo', 'www.example.com', False, False,
                      'md5', 2345, 234, True),
        })


class _Context(object):
    def __init__(self):
        self.actions = []

    def action(self, *args, **kw):
        self.actions.append((args, kw))
