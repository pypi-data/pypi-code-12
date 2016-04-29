from zope.interface import implementer

try:
    from pyramid_nacl_session import EncryptedSerializer
except ImportError:
    _HAS_PYRAMID_NACL_SESSION = False
else:
    _HAS_PYRAMID_NACL_SESSION = True

from .interfaces import ISignedSessionCookieConfig


@implementer(ISignedSessionCookieConfig)
class SignedSessionCookieConfig(object):

    def __init__(self, 
                 secret,
                 salt=None,
                 cookie_name='session',
                 max_age=None,
                 path=None,
                 domain=None,
                 secure=True,
                 http_only=True,
                 hash_algorithm=None,
                 timeout=None,
                 reissue_time=None,
                 encrypt=False,
                ):
        self.secret = secret
        self.salt = salt
        self.cookie_name = cookie_name
        self.max_age = max_age
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.hash_algorithm = hash_algorithm
        self.timeout = timeout
        self.reissue_time = reissue_time
        if encrypt and not _HAS_PYRAMID_NACL_SESSION:
            raise ValueError('Install pyramid_nacl_session!')
        self.encrypt = encrypt

    def getCookieAttrs(self):
        """-> dict for configuring the Pyramid session cookie class."""
        result = dict([(key, value) for key, value in self.__dict__.items()
                       if value is not None])
        if result.pop('encrypt'):
            result['serializer'] = EncryptedSerializer(self.secret)
            if 'secret' in result:
                del result['secret']
            if 'salt' in result:
                del result['salt']
        result['httponly'] = result.pop('http_only')
        if 'hash_algorithm' in result:
            result['hashalg'] = result.pop('hash_algorithm')
        return result
