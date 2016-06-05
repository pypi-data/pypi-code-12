#!/usr/bin/env python3

import functools


class HaikerError(Exception):
    """Raised when something has gone wrong."""
    def __init__(self, error):
        super().__init__()
        self._error = error

    @property
    def causal_error(self):
        """An exception object which has raised this error"""
        return self._error

    def __str__(self):
        return str(self._error)

    @classmethod
    def replace(cls, func):
        """Return a function which has the same behavior as func but
        raises this exception instead of raising other exception.
        """
        @functools.wraps(func)
        def call(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except cls:
                raise
            except Exception as e:
                raise cls(e) from e
        return call
