from logging import Handler
import redis


class RedisHandler(Handler):
    '''
    A handler to print log to a redis list
    '''

    def __init__(self, host, port, db, key):
        self.pool = redis.ConnectionPool(
            host=host,
            port=port,
            db=db,
        )
        self.key = key
        super(RedisHandler, self).__init__()

    def emit(self, record):
        try:
            msg = self.format(record)
            r = redis.Redis(connection_pool=self.pool)
            r.lpush(self.key, msg)
        except Exception:
            self.handleError(record)
