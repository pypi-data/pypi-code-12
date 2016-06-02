import abc
import time
from threading import Thread
from datetime import datetime, timedelta

import sqlalchemy

from series.logging import Logging

from tryp import List

from series.errors import SeriesDException
from series.condition import HandlerCondition, StrictCondition


class Handler(Thread, Logging, metaclass=abc.ABCMeta):

    def __init__(self, interval, description, cooldown=0):
        self._interval = interval
        self._description = description
        super().__init__(name=self._description)
        self._running = True
        self._initial_wait = 5
        self._failures = 0
        self._cooldown = cooldown
        self._last_check = {}

    def run(self):
        self.log.info('Starting {}.'.format(self._description))
        try:
            self._sanity_check()
        except SeriesDException as e:
            self.log.error('Shutting down {} with reason: {}'.format(
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
            self.log.debug(e)
        except Exception as e:
            self._failure(e)
        else:
            if success:
                self._success()

    def _check(self):
        with self._lock:
            return self._current.effect(self._process).is_just

    def _process(self, item):
        if hasattr(item, 'id'):
            self._last_check[item.id] = time.time()
        self._handle(item)

    @property
    def _next_check(self):
        return datetime.now() + timedelta(seconds=self._interval)

    def _handle(self, task):
        pass

    @property
    def _current(self):
        return self._choose(self._qualified)

    def _choose(self, qualified):
        return qualified.head

    def _cool(self, item):
        return (not hasattr(item, 'id') or time.time() -
                self._last_check.get(item.id, 0) > self._cooldown)

    def activate_id(self, id):
        if id in self._last_check:
            del self._last_check[id]

    @abc.abstractproperty
    def _candidates(self):
        ...

    def _qualify(self, candidate):
        return self._conditions.ev(candidate)

    @property
    def _qualified(self):
        return List.wrap(self._candidates)\
            .filter(self._cool)\
            .filter(self._qualify)

    def explain(self, item):
        cond = self._conditions.describe(item, target=True)
        return dict(name=self._description, cond=cond)

    @property
    def _conditions(self) -> HandlerCondition:
        return StrictCondition(False)

    def _commit(self):
        pass

    def _sanity_check(self):
        pass

    def _failure(self, exc):
        self._failures += 1
        import traceback
        self.log.error('Error in {}:'.format(self._description))
        self.log.error(exc)
        traceback.print_exc()
        if self._failures >= 20:
            msg = '20 failures in a row in {}, shutting down.'
            self.log.error(msg.format(self._description))
            self.stop()

    def _success(self):
        self._failures = 0

    @property
    def _lock(self):
        raise NotImplementedError('Handler._lock')

__all__ = ['Handler']
