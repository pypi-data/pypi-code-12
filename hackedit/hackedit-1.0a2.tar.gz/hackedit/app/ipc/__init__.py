"""
A small library for inter-process communication inside PyQt5 applications.

The API is similar to the multiprocessing API but integrate much better with
the Qt event loop. It also works more reliably on Windows and OSX when the
native launcher is used.

"""
from .client import Process

__all__ = [
    'Process'
]
