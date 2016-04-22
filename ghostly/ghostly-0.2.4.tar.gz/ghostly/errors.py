# -*- coding: utf-8 -*-
"""
    ghostly.errors
    ~~~~~~~~~~~~~~

    All local errors that ghostly raises.

"""
from __future__ import absolute_import, print_function, unicode_literals


__all__ = ['GhostlyError', 'DriverDoesNotExistError', 'GhostlyTestFailed']


class GhostlyError(Exception):
    """
    Ghostly error, which all Ghostly errors inherit.
    """
    pass


class DriverDoesNotExistError(GhostlyError):
    """
    Raised when :py:meth:`Ghostly.__init__` can't load a specific driver.
    """
    pass


class GhostlyTestFailed(GhostlyError):
    pass


class GhostlyTimeoutError(GhostlyError):
    """
    Raised when a timeout occurs within Ghostly.
    """
    pass
