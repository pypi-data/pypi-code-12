from __future__ import print_function, division, absolute_import

from threading import Thread

from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado import gen

from ..utils import sync, ignoring
from ..executor import Executor
from ..scheduler import Scheduler
from ..worker import Worker


class Loop(object):
    def __init__(self, n_workers=0, loop=None, start=True, scheduler_port=8976, **kwargs):
        self.loop = loop or IOLoop()
        self.scheduler = Scheduler(loop=loop, **kwargs)
        self.scheduler.start(scheduler_port)
        self.workers = []
        for i in range(n_workers):
            self.start_worker()

        if start:
            self._thread = Thread(target=self.loop.start)
            self._thread.daemon = True
            self._thread.start()

    @gen.coroutine
    def _start_worker(self, port=0, **kwargs):
        w = Worker(self.scheduler.ip, self.scheduler.port, loop=self.loop, **kwargs)
        yield w._start(port)
        self.workers.append(w)
        return w

    def start_worker(self, port=0, **kwargs):
        return sync(self.loop, self._start_worker, port, **kwargs)

    @gen.coroutine
    def _stop_worker(self, w):
        yield w._close()
        self.workers.remove(w)

    def stop_worker(self, w):
        sync(self.loop, self._stop_worker, w)

    @gen.coroutine
    def _close(self):
        with ignoring(gen.TimeoutError, StreamClosedError, OSError):
            yield self.scheduler.close()
        for w in self.workers:
            with ignoring(gen.TimeoutError, StreamClosedError, OSError):
                yield w._close()
        self.workers.clear()

    def close(self):
        sync(self.loop, self._close)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
