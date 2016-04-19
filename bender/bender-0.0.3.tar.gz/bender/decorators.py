from __future__ import unicode_literals
from functools import wraps


def next_step(method_name):
    def decorator(method):
        @wraps(method)
        def wrapper(self, *args, **kwargs):
            success = method(self, *args, **kwargs)
            if success:
                self.redis.set(self.redis_prefix + 'users:' + str(self._from['id']) + ':next_step', method_name)
            return success
        return wrapper
    return decorator


def final_step(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        success = method(self, *args, **kwargs)
        if success:
            self._end_transaction()
        return success
    return wrapper
