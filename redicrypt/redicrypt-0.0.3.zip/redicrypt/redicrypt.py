from Crypto.Cipher import AES
import random
import string
import redis
import os

DEFAULT_IV_PATH = './ivr'
DEFAULT_KEY_PATH = './key'


# utility function used across all methods here to make sure defaults are read if no path is specified
def get_paths(key, ivr):
    _key = DEFAULT_KEY_PATH if key is None else key
    _ivr = DEFAULT_IV_PATH if ivr is None else ivr
    return _key, _ivr


def initialize_encryption(key_path=None, ivr_path=None):
    """ This function (re)generates the keys we'll use for encryption and stores them on the file system."""
    key_path, ivr_path = get_paths(key_path, ivr_path)
    # We are using w+ here because during initialization, we are absolutely going to want to truncate it
    # and write a new key.
    with open(key_path, "w+") as key:
        key.write(''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))
    # with CFB, the IV must be at least length of 16
    with open(ivr_path, "w+") as ivr:
        ivr.write(''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16)))


# private method
def get_hash(key_path, ivr_path):
    """ This is a utility function to grab the values needed to produce the AES key"""
    with open(key_path, "r+") as key_file:
        key = key_file.read()
    with open(ivr_path, "r+") as ivr_file:
        ivr = ivr_file.read()
    return AES.new(key, AES.MODE_CFB, ivr)


def set(name, value, key_path=None, ivr_path=None, overredis=None):
    """ This sets a value encrypted in redis """
    key_path, ivr_path = get_paths(key_path, ivr_path)
    aes = get_hash(key_path, ivr_path)
    ciphertext = aes.encrypt(value)
    r = overredis if overredis is not None else loadconfiguration()
    r.set(name, ciphertext)


def get(name, key_path=None, ivr_path=None, overredis=None):
    """ This gets a value that is encrypted in redis."""
    key_path, ivr_path = get_paths(key_path, ivr_path)
    r = overredis if overredis is not None else loadconfiguration()
    cipher = r.get(name)
    aes = get_hash(key_path, ivr_path)
    return aes.decrypt(cipher)


def getrange(name, start, end, key_path=None, ivr_path=None, overredis=None):
    # this requires a get, and then the range is returned.
    key_path, ivr_path = get_paths(key_path, ivr_path)
    r = overredis if overredis is not None else loadconfiguration()
    encrypted = r.get(name)
    aes = get_hash(key_path, ivr_path)
    decrypted = aes.decrypt(encrypted)
    return decrypted[start:end]


def hget(name, field, key_path=None, ivr_path=None, overredis=None):
    key_path, ivr_path = get_paths(key_path, ivr_path)
    r = overredis if overredis is not None else loadconfiguration()
    encrypted = r.hget(name, field)
    aes = get_hash(key_path, ivr_path)
    return aes.decrypt(encrypted)


def test_availability(host=None):
    test = loadconfiguration(host)
    return True if test is not None else False


def loadconfiguration(host=None):
    try:
        if host is None:
            host = os.environ['REDIS_ENDPOINT']
            return redis.StrictRedis(host=host)
    except Exception, e:
        raise e
