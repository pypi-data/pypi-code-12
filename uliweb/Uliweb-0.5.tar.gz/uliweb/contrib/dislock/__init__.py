from uliweb import functions
from uliweb.utils.common import get_uuid

def get_lock(key, value=None, expiry_time=60):
    redis = functions.get_redis()
    value = value or get_uuid()
    return redis.set(key, value, ex=expiry_time, nx=True)