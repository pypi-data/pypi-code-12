import os
import logging
import signal
import json
from datetime import datetime
import pytz
from concurrent.futures import ThreadPoolExecutor

from tornado import gen, concurrent
from tornado.options import options
from tornado.locks import Event

import sqlalchemy as sa

from . import models
from .comb import DummyFrequencyComb, FrequencyComb
from .web import make_app
from .stores import store

logger = logging.getLogger('brush')

try:
    import redis
except ImportError:
    logger.warning('redis not found... will not try to write to Redis.')
    redis = None


class Sweep(object):
    """Get data from the frequency comb XMLRPC server and log it to a
    database.

    """
    def __init__(self, comb):
        assert isinstance(comb, (DummyFrequencyComb, FrequencyComb))
        self.comb = comb
        self.executor = ThreadPoolExecutor(max_workers=1)

        # Initialize databases
        self.indices = []
        self._old_indices = []
        self.engine = sa.create_engine(options.sql_url)
        self.table = models.initialize(self.comb, self.engine)
        self._init_redis()

        # Start the web server
        if not os.environ.get('BRUSH_NOSERVER', False):
            self.done = Event()
            self.app = make_app(self.engine, prefix=options.server_url_prefix)
            self.app.listen(options.server_port)
            signal.signal(signal.SIGINT, lambda num, frame: self.done.set())
            logger.info('Listening on port ' + str(options.server_port))

    def _init_redis(self):
        """Connect to redis if applicable."""
        self.redis = None
        if redis is not None:
            try:
                self.redis = redis.StrictRedis(host=options.redis_host,
                                               port=options.redis_port,
                                               password=options.redis_password)
                self.redis.ping()
            except Exception:
                logger.error(
                    'Error configuring or connecting to Redis. Disabling.')
                self.redis = None

    @concurrent.run_on_executor
    def write(self, data):
        try:
            with self.engine.connect() as conn:
                ins = self.table.insert()
                conn.execute(ins, **data)
        except Exception as e:
            logger.error(e)

    @gen.coroutine
    def run(self):
        """Periodically polls the comb server for data."""
        last_timestamp = None
        while not self.done.is_set():
            data = self.comb.get_data()
            timestamp = data['timestamp']

            # Don't rewrite data
            if timestamp == last_timestamp:
                yield gen.sleep(0.01)
                continue
            last_timestamp = timestamp

            data = {key.replace('.', '_').lower(): data[key] for key in data}
            store.append(data)
            if self.redis is not None:
                jsonized = json.dumps(data)
                pipe = self.redis.pipeline()
                pipe.set('brush', jsonized)
                pipe.publish('brush', jsonized)
                pipe.execute()

            locked = all([data['system_locked'],  # mode locked (?)
                          data['lb1_status'],     # reprate locked
                          data['lb2_status']])    # offset locked
            if locked or options.save_when_unlocked:
                data['timestamp'] = datetime.fromtimestamp(timestamp, pytz.utc)
                self.write(data)

            if options.offline:
                yield gen.sleep(1)
