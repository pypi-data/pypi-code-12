import hashlib
import hmac


def get_hmac(secret, data):
    sig = hmac.new(bytes(secret), bytes(data), hashlib.sha1).hexdigest()
    return sig
