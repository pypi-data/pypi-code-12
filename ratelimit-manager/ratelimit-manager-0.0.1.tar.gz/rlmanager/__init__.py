# -*- coding: utf-8 -*-
import time

import numpy as np


__all__ = ('IntRingBuffer', 'RateLimit', 'RateLimitManager', 'RateLimitError')


class IntRingBuffer(object):
    def __init__(self, size):
        self._size = size
        self._buffer = np.ndarray((size,), dtype=np.int64)

        self._head = 0
        self._next = 0
        self._count = 0

    @property
    def size(self):
        return self._size

    def __len__(self):
        return self._count

    def popleft(self):
        if len(self) == 0:
            raise StandardError('no item')

        ret = self._buffer[self._head]
        self._incr_head()

        self._count -= 1
        return ret

    def append(self, number):
        if len(self) == self._size:
            self._incr_head()
        else:
            self._count += 1

        self._buffer[self._next] = number
        self._incr_next()

    def _incr_head(self):
        self._head += 1
        if self._head == self._size:
            self._head = 0

    def _incr_next(self):
        self._next += 1
        if self._next == self._size:
            self._next = 0

    def __getitem__(self, idx):
        if len(self) <= idx:
            raise StandardError('access error: index=' + idx)

        realidx = self._head + idx
        if self._size <= realidx:
            realidx = realidx - self._size

        return self._buffer[realidx]

    def __iter__(self):
        def _generator():
            for i in xrange(len(self)):
                yield self[i]

        return _generator()


class RateLimitError(Exception):
    pass


class RateLimitManager(object):
    def __init__(self, rules):
        self._rate_limits = [ RateLimit(lim, d) for lim, d in rules ]

    def __repr__(self):
        return '<RateLimitManager rules=(%s)>' % ', '.join([str(r) for r in self._rate_limits])

    def __str__(self):
        return repr(self)

    def is_all_tick_ok(self):
        for limit in self._rate_limits:
            if not limit.is_tick_ok():
                return (False, limit)
        return (True, None)

    def tick_all(self):
        is_ok, error_rule = self.is_all_tick_ok()
        if not is_ok:
            exception = RateLimitError('cannot tick')
            exception.rule = error_rule
            raise exception

        for limit in self._rate_limits:
            limit.tick_nocheck()  # less computation


class RateLimit(object):
    def __init__(self, limit_count, duration_msec):
        assert 0 < limit_count
        assert 0 < duration_msec
        self._limit_count = limit_count
        self._duration_msec = duration_msec
        self._buffer = self._build_ring_buffer()

    def __repr__(self):
        return '<RateLimit limit=%d, duration=%dmsec>' % (self._limit_count, self._duration_msec)

    def __str__(self):
        return repr(self)

    @property
    def limit_count(self):
        return self._limit_count

    @property
    def duration_msec(self):
        return self._duration_msec

    def _now(self):
        return round(time.time() * 1000)

    def _build_ring_buffer(self):
        return IntRingBuffer(self._limit_count + 1)

    def reset(self):
        self._buffer = self._build_ring_buffer()

    def count_for_now(self):
        buflen = len(self._buffer)
        if buflen == 0:
            return 0
        now = self._now()
        threshold = now - self._duration_msec
        insert_idx = np.searchsorted(self._buffer, threshold)
        return buflen - insert_idx

    def is_tick_ok(self):
        count = self.count_for_now()
        return not (count == self._limit_count)

    def tick(self):
        now = self._now()
        if not self.is_tick_ok():
            err = RateLimitError(
                'cannot tick, already called %d times in %dmsec' % (self._limit_count, self._duration_msec))
            err.rule = self
            raise err
        self._buffer.append(now)

    def tick_nocheck(self):
        self._buffer.append(now)
