"""
Counting Lock
=============
A (threading) lock that keeps a count of the number of threads currently
waiting to acquire it. It wraps Python's `threading.Lock`, with an
additional method `waiting_to_acquire`, which returns the number of
waiting threads.

Legalese
--------
Copyright (c) 2016 Genome Research Ltd.

Author: Christopher Harrison <ch12@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from threading import Lock

class CountingLock(object):
    """ Lock that keeps count of threads waiting to acquire itself """
    def __init__(self, *args, **kwargs):
        """ Wraps Lock constructor """
        self._lock = Lock(*args, **kwargs)

        self._wait_lock = Lock()
        self._waiting = 0

    def acquire(self, *args, **kwargs):
        """ Wraps Lock.acquire """
        with self._wait_lock:
            self._waiting += 1

        self._lock.acquire(*args, **kwargs)

        with self._wait_lock:
            self._waiting -= 1

    def release(self):
        """ Wraps Lock.release """
        self._lock.release()

    def waiting_to_acquire(self) -> int:
        """ Return the number of threads waiting to acquire the lock """
        with self._wait_lock:
            return self._waiting

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()
