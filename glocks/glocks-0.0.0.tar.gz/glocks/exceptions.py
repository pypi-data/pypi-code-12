from redis.exceptions import RedisError


class LockError(RedisError):
    pass


class ClientError(LockError):
    pass
