import unittest


class SignedSessionCookieConfigTests(unittest.TestCase):

    def _getTargetClass(self):
        from ..config import SignedSessionCookieConfig
        return SignedSessionCookieConfig

    def _makeOne(self, *args, **kw):
        return self._getTargetClass()(*args, **kw)

    def test_class_conforms_to_ISignedSessionCookieConfig(self):
        from zope.interface.verify import verifyClass
        from ..interfaces import ISignedSessionCookieConfig
        verifyClass(ISignedSessionCookieConfig, self._getTargetClass())

    def test_instance_conforms_to_ISignedSessionCookieConfig(self):
        from zope.interface.verify import verifyObject
        from ..interfaces import ISignedSessionCookieConfig
        verifyObject(ISignedSessionCookieConfig,
                     self._makeOne('SECRET'))

    def test_ctor_minimal(self):
        config = self._makeOne('SECRET')
        self.assertEqual(config.secret, 'SECRET')
        self.assertEqual(config.salt, None)
        self.assertEqual(config.cookie_name, 'session')
        self.assertEqual(config.max_age, None)
        self.assertEqual(config.path, None)
        self.assertEqual(config.domain, None)
        self.assertEqual(config.secure, True)
        self.assertEqual(config.http_only, True)
        self.assertEqual(config.hash_algorithm, None)
        self.assertEqual(config.timeout, None)
        self.assertEqual(config.reissue_time, None)

    def test_ctor_explicit(self):
        config = self._makeOne('SECRET', 'SALT', 'COOKIE', 1234,
                               '/foo', 'www.example.com', False, False,
                               'md5', 2345, 234)
        self.assertEqual(config.secret, 'SECRET')
        self.assertEqual(config.salt, 'SALT')
        self.assertEqual(config.cookie_name, 'COOKIE')
        self.assertEqual(config.max_age, 1234)
        self.assertEqual(config.path, '/foo')
        self.assertEqual(config.domain, 'www.example.com')
        self.assertEqual(config.secure, False)
        self.assertEqual(config.http_only, False)
        self.assertEqual(config.hash_algorithm, 'md5')
        self.assertEqual(config.timeout, 2345)
        self.assertEqual(config.reissue_time, 234)

    def test_ctor_w_encrypt_wo_pyramid_nacl_session(self):
        from zope2.sessioncookie import config as MUT
        with _Monkey(MUT, _HAS_PYRAMID_NACL_SESSION=False):
            with self.assertRaises(ValueError):
                self._makeOne('SECRET', encrypt=True)

    def test_ctor_w_encrypt_w_pyramid_nacl_session(self):
        from zope2.sessioncookie import config as MUT
        SECRET = b'\x01' * 32
        with _Monkey(MUT, _HAS_PYRAMID_NACL_SESSION=True):
            config = self._makeOne(SECRET, encrypt=True)
            self.assertTrue(config.encrypt)

    def test_getCookieAttrs_defaults(self):
        config = self._makeOne('SECRET')
        self.assertEqual(config.getCookieAttrs(),
                         {'secret': 'SECRET',
                          'cookie_name': 'session',
                          'secure': True,
                          'httponly': True,
                         })

    def test_getCookieAttrs_explicit(self):
        config = self._makeOne('SECRET', 'SALT', 'COOKIE', 1234,
                               '/foo', 'www.example.com', False, False,
                               'md5', 2345, 234)
        self.assertEqual(config.getCookieAttrs(),
                         {'secret': 'SECRET',
                          'salt': 'SALT',
                          'cookie_name': 'COOKIE',
                          'max_age': 1234,
                          'path': '/foo',
                          'domain': 'www.example.com',
                          'secure': False,
                          'httponly': False,
                          'hashalg': 'md5',
                          'timeout': 2345,
                          'reissue_time': 234,
                         })

    def test_getCookieAttrs_w_encrypt(self):
        from pyramid_nacl_session import EncryptedSerializer
        SECRET = b'\x01' * 32
        config = self._makeOne(SECRET, 'SALT', 'COOKIE', 1234,
                               '/foo', 'www.example.com', False, False,
                               'md5', 2345, 234, True)
        attrs = config.getCookieAttrs()
        serializer = attrs.pop('serializer')
        self.assertTrue(isinstance(serializer, EncryptedSerializer))
        self.assertEqual(attrs,
                         {'cookie_name': 'COOKIE',
                          'max_age': 1234,
                          'path': '/foo',
                          'domain': 'www.example.com',
                          'secure': False,
                          'httponly': False,
                          'hashalg': 'md5',
                          'timeout': 2345,
                          'reissue_time': 234,
                         })


class _Monkey(object):
    # context-manager for replacing module names in the scope of a test.

    def __init__(self, module, **kw):
        self.module = module
        self.to_restore = dict([(key, getattr(module, key)) for key in kw])
        for key, value in kw.items():
            setattr(module, key, value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for key, value in self.to_restore.items():
            setattr(self.module, key, value)
