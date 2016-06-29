"""Web interface for brush."""

import os.path
import logging
from concurrent.futures import ThreadPoolExecutor
import json
from decimal import Decimal
from datetime import datetime
import pytz
from six.moves import cStringIO as StringIO

from tornado import gen
from tornado.options import options
from tornado.web import (Application, RequestHandler, MissingArgumentError)
from tornado.concurrent import run_on_executor
from tornado.escape import url_unescape
from tornadose.stores import DataStore
from tornadose.handlers import EventSource

from . import models
from .models import select_timeseries
from .stores import store

sse_store = DataStore()
store.callback = lambda data: sse_store.submit(json.dumps(data))

logger = logging.getLogger('web')

base_dir = os.path.dirname(__file__)
default_static_path = os.path.abspath(
    os.path.join(base_dir, 'static'))
template_path = os.path.abspath(
    os.path.join(base_dir, 'templates'))


class IndexHandler(RequestHandler):
    def get(self):
        """Render the web UI."""
        self.render('index.html')


class DataHandler(RequestHandler):
    executor = ThreadPoolExecutor(max_workers=4)

    def initialize(self, engine, table):
        self.engine = engine
        self.table = table

    def _jsonize(self, data):
        if isinstance(data[0], datetime):
            data = [(dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds() for dt in data]
        elif isinstance(data[0], Decimal):
            data = [float(d) for d in data]
        return data

    @run_on_executor
    def get_data(self, start, stop=None, keys=None):
        """Retrieve data from the database server."""
        with self.engine.connect() as conn:
            sel = select_timeseries(self.table, start, stop, keys)
            rows = conn.execute(sel).fetchall()
        if len(rows) == 0:
            return dict(error='No data; try an earlier start time')
        columns = self.table.columns.keys() if keys is None else keys
        row_data = list(zip(*rows))
        data = {col: self._jsonize(row_data[i]) for i, col in enumerate(columns)}
        return data

    @gen.coroutine
    def get(self):
        """Get data starting from the timestamp ``start`` up until the
        timestamp ``stop``. Timestamps must be given as seconds since
        the epoch (i.e., Unix time) and passed as query arguments in the
        ``GET`` request.

        If only ``start`` is given, the stop point is the current time.

        Example::

           http://localhost:8090/data?start=1465727734.4149404

        .. note:: The database stores timestamps in UTC.

        """
        try:
            start_str = url_unescape(self.get_query_argument('start'))
            if not len(start_str):
                raise MissingArgumentError('No start given')
            start = float(start_str)
        except MissingArgumentError:
            self.send_error(400)
            return
        except TypeError:
            self.write(dict(error=('Invalid start timestamp: %s' % start_str)))
            return

        try:
            stop_str = url_unescape(self.get_query_argument('stop'))
            stop = float(stop_str)
        except MissingArgumentError:
            stop = None
        except TypeError:
            self.write(dict(error=('Invalid stop timestamp: %s' % stop_str)))
            return

        try:
            keys = self.get_query_argument('keys')
            keys = keys.split(',')
        except MissingArgumentError:
            keys = None

        try:
            data = yield gen.maybe_future(self.get_data(start, stop, keys))
            stream = StringIO(json.dumps(data, sort_keys=True))
            self.set_header('content-type', 'application/json')
            while True:
                chunk = stream.read(1024)
                if not chunk:
                    break
                self.write(chunk)
                self.flush()
                yield gen.moment
        except Exception as e:
            self.send_error(400)
            logger.error(str(e))
            raise(e)


class QueryHandler(RequestHandler):
    def get(self, key):
        """Return the most recent value for the requested key."""
        try:
            value = store.get()[key]
            self.write({
                key: value,
                'error': None
            })
        except KeyError:
            self.write({'error': 'No such key'})


class CurrentDataHandler(RequestHandler):
    def get(self):
        """Return the most recent data."""
        data = store.get()
        data['error'] = None
        self.write(data)


class RecentDataHandler(RequestHandler):
    def get(self):
        """Return all data currently in the store."""
        try:
            data = store.get(amount=-1)
            data['error'] = None
        except:
            data = dict(error="Server error. Check logs.")
        self.write(data)


class MetaDataHandler(RequestHandler):
    def get(self):
        """Return comb metadata.

        Metadata includes types and descriptions of all data types.

        """
        self.write(store.metadata)


class KeysHandler(RequestHandler):
    def get(self):
        """Return all data keys."""
        self.write(dict(keys=store.keys()))


def make_app(engine, prefix=None, static_path=default_static_path):
    """Initialize the Tornado web app.

    Parameters
    ----------
    engine
        SQLAlchemy engine
    prefix : str or None
        URL prefix for routing
    static_path : str
        Path to static files (JS, CSS, images, etc.)

    """
    handlers = [
        ['/', IndexHandler],
        ['/data', DataHandler, dict(engine=engine, table=models.brush)],
        ['/data/current', CurrentDataHandler],
        ['/data/recent', RecentDataHandler],
        ['/data/query/(.*)', QueryHandler],
        ['/data/metadata', MetaDataHandler],
        ['/data/keys', KeysHandler],
        ['/query/(.*)', QueryHandler],  # kept for backwards compatibility
        ['/stream', EventSource, dict(store=sse_store)]
    ]
    if prefix not in [u'', None]:
        if prefix[0] != '/':
            prefix = '/' + prefix
        for handler in handlers:
            route = handler[0]
            if route == '/':
                handler[0] = prefix
            else:
                handler[0] = prefix + route

    app = Application(
        handlers,
        compress_response=True,
        template_path=template_path,
        static_path=static_path,
        debug=options.debug
    )
    return app
