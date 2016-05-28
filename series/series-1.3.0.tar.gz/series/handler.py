import time
from threading import Thread
from datetime import datetime, timedelta

import sqlalchemy

from tek import logger
from tek.tools import find

from series.get.errors import SeriesDException


class Handler(Thread):

    def __init__(self, interval, description, cooldown=0):
        self._interval = interval
        self._description = description
        super(Handler, self).__init__(name=self._description)
        self._running = True
        self._initial_wait = 5
        self._failures = 0
        self._cooldown = cooldown
        self._last_check = {}

    def run(self):
        logger.info('Starting {}.'.format(self._description))
        try:
            self._sanity_check()
        except SeriesDException as e:
            logger.error('Shutting down {} with reason: {}'.format(
                self._description, e))
        else:
            self._main_loop()

    def _main_loop(self):
        next_check = datetime.now() + timedelta(seconds=self._initial_wait)
        while self._running:
            if datetime.now() > next_check:
                self._check_error_wrapper()
                next_check = self._next_check
            time.sleep(1)

    def stop(self):
        self._running = False

    def _check_error_wrapper(self):
        success = False
        try:
            success = self._check()
        except sqlalchemy.exc.InvalidRequestError as e:
            logger.debug(e)
        except Exception as e:
            self._failure(e)
        else:
            if success:
                self._success()

    def _check(self):
        with self._lock:
            current = self._current
            if current is not None:
                if hasattr(current, 'id'):
                    self._last_check[current.id] = time.time()
                self._handle(current)
                return True

    @property
    def _next_check(self):
        return datetime.now() + timedelta(seconds=self._interval)

    def _handle(self, task):
        pass

    @property
    def _current(self):
        candidates = [c for c in self._candidates if self._cool(c)]
        return find(self._qualify, candidates)

    def _cool(self, item):
        return (not hasattr(item, 'id') or time.time() -
                self._last_check.get(item.id, 0) > self._cooldown)

    @property
    def _candidates(self):
        raise NotImplementedError('Handler._candidates')

    def _qualify(self, candidate):
        return True

    def _commit(self):
        pass

    def _sanity_check(self):
        pass

    def _failure(self, exc):
        self._failures += 1
        import traceback
        logger.error('Error in {}:'.format(self._description))
        logger.error(exc)
        traceback.print_exc()
        if self._failures >= 20:
            msg = '20 failures in a row in {}, shutting down.'
            logger.error(msg.format(self._description))
            self.stop()

    def _success(self):
        self._failures = 0

    @property
    def _lock(self):
        raise NotImplementedError('Handler._lock')

__all__ = ['Handler']
