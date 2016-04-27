import sha
import base64
import os

from Crypto.Cipher import AES
from Crypto.Protocol.AllOrNothing import AllOrNothing
from cPickle import loads, dumps

from M2Crypto import SMIME, X509, BIO

from django.conf import settings

class Lockable(object):
    """A non-mutable, encrypted dictionary wrapper, designed for pickling.

    A one-way hash of the keys from the dictionary is also maintained; this allows us to raise KeyErrors
    rather than Lockable.IsLocked if a value is requested when the dictionary is locked.
    """

    class IsLocked(Exception):
        pass

    class InvalidPassphrase(Exception):
        pass

    def __init__(self, d):
        self.plaindict=d
        plaintext=dumps(dict(d))

        self.key_hashes=set([self.hash_key(k) for k in d.keys()])

        s = SMIME.SMIME()

        x509 = X509.load_cert(settings.RSA_CERTIFICATE)
        sk = X509.X509_Stack()
        sk.push(x509)
        s.set_x509_stack(sk)
        s.set_cipher(SMIME.Cipher('des_ede3_cbc'))

        p7 = s.encrypt(BIO.MemoryBuffer(plaintext), flags=SMIME.PKCS7_BINARY)

        out = BIO.MemoryBuffer()
        p7.write(out)
        self.ciphertext=out.read()

    def unlock(self, passphrase):
        s=SMIME.SMIME()
        try:
            s.load_key(settings.RSA_KEYPAIR, settings.RSA_CERTIFICATE, lambda *args: passphrase)
        except:
            raise Lockable.InvalidPassphrase('The supplied passhrase was incorrect.')

        p7=SMIME.load_pkcs7_bio(BIO.MemoryBuffer(self.ciphertext))
        plaintext=s.decrypt(p7)

        self.plaindict=loads(plaintext)

    def lock(self):
        try:
            del(self.plaindict)
        except AttributeError:
            pass

    def locked(self):
        return not hasattr(self, 'plaindict')

    def hash_key(self, key):
        return sha.new(key).digest()

    def __getitem__(self, key):
        try:
            return self.plaindict[key]
        except AttributeError:
            if self.hash_key(key) not in self.key_hashes:
                raise KeyError(key)
            raise Lockable.IsLocked("The lock has not been decrypted")

    def __contains__(self, key):
        try:
            return key in self.plaindict
        except AttributeError:
            return self.hash_key(key) in self.key_hashes

    def __getstate__(self):
        """Lock before pickling so that sensitive data is never pickled."""
        self.lock()
        return self.__dict__

def symmetric_encrypt(obj):
    """Encrypts a serialized object obj using a symmetric cipher and random key,
    returning the ciphertext (base64-encoded) and the key (similarly encoded)."""

    key = os.urandom(32)
    cipher = AES.new(key, AES.MODE_CBC)
    aon = AllOrNothing(AES)
    blocks = ''.join(aon.digest(dumps(obj)))
    return base64.encodestring(key), base64.encodestring(cipher.encrypt(blocks))

def symmetric_decrypt(key, data):
    """Decrypts and deserialized an object from base64-encoded key/ciphertext.
    """
    cipher = AES.new(base64.decodestring(key), AES.MODE_CBC)
    plain = cipher.decrypt(base64.decodestring(data))
    blocks = []
    while plain:
        blocks.append(plain[:16])
        plain = plain[16:]
    aon = AllOrNothing(AES)
    return loads(aon.undigest(blocks))
