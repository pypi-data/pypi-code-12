import logging
import random
from uuid import uuid4
from pycoin import ecdsa
from pycoin.key import Key
from pycoin.tx.script import der
from ambisafe.crypt import Crypt

logger = logging.getLogger('ambisafe')
SIGHASH_ALL = 1
order = ecdsa.generator_secp256k1.order()


class Container(object):
    def __init__(self, public_key, data, iv, salt):
        """Creates container.
        :param public_key: Public key
        :param data: Encrypted private_key
        :param iv: IV
        :param salt: Salt
        :return: Container
        """
        self.publicKey = public_key
        self.data = data
        self.iv = iv
        self.salt = salt

    @classmethod
    def generate_key_pair(cls):
        key = Key(random.SystemRandom().randrange(1, order))
        private_key = format(key.secret_exponent(), 'x')
        if len(private_key) % 2:
            private_key = '0' + private_key
        public_key = key.sec_as_hex()
        return private_key, public_key

    @classmethod
    def generate(cls, secret):
        """Generating new container encrypted with secret
        :param secret:
        :type secret: basestring
        :param private_key:
        :type private_key: basestring
        :return: Container
        """
        private_key, public_key = cls.generate_key_pair()
        encrypted_private_key, iv, salt = cls._encrypt(private_key, secret)
        return cls(public_key, encrypted_private_key, iv, salt)

    @classmethod
    def create_from_private_key(cls, private_key, secret):
        """Create new container from private_key encrypted with secret
        :param private_key:
        :type private_key: basestring
        :param secret:
        :type secret: basestring
        :return: Container
        """
        key = Key(int(private_key, 16))
        public_key = key.sec_as_hex()
        encrypted_private_key, iv, salt = cls._encrypt(private_key, secret)
        return cls(public_key, encrypted_private_key, iv, salt)

    @classmethod
    def _encrypt(cls, private_key, secret):
        crypt = Crypt(secret)
        salt = str(uuid4())
        iv, encrypted_private_key = crypt.encrypt(private_key, salt)
        return encrypted_private_key, iv, salt

    @classmethod
    def from_server_response(cls, publicKey=None, data=None, iv=None, salt=None, public_key=None):
        """Creating Container object from Ambisafe KeyServer response
        :param publicKey: For backward compatibility
        :param data:
        :param iv:
        :param salt:
        :param public_key:
        :return:
        """
        if not public_key and not publicKey:
            raise ValueError('public_key must be provided')
        if not public_key:
            public_key = publicKey
        return cls(public_key, data, iv, salt)

    def get_private_key(self, secret):
        """Get decrypted private key from Container using secret
        :param secret:
        :return: str
        """
        crypt = Crypt(secret)
        private_key = crypt.decrypt(self.data, self.salt, self.iv)
        if not private_key:
            raise ValueError('Wrong secret')
        return private_key

    def sign(self, message, private_key):
        """Sign message with private key
        :param message:
        :param private_key:
        :return: str
        """
        key = Key(int(private_key, 16))
        r, s = ecdsa.sign(ecdsa.generator_secp256k1, key.secret_exponent(), int(message, 16))
        if s + s > order:
            s = order - s
        sig = der.sigencode_der(r, s) + chr(SIGHASH_ALL)
        return sig.encode('hex')

    def __getitem__(self, item):
        return self.__dict__[item]

    def as_response(self):
        """Get container dict in response format
        :return: dict
        """
        return self.__dict__

    def as_request(self):
        """Get container dict in request format
        :return: dict
        """
        container = self.__dict__
        # work around different request and response formats
        container['public_key'] = container.pop('publicKey')
        return container

    def __repr__(self):
        return u'<Container public_key="{}" data="{}" iv="{}" salt="{}">'.format(
            self.publicKey, self.data, self.iv, self.salt
        )
