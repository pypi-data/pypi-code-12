# -*- coding: utf-8 -*-
# Time-stamp: < utils.py (2016-02-14 11:05) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

"""Utility functions and classes."""

import collections
import io
import logging
import logging.config
import os
import os.path
import sys
import threading
import types

from summer.ex import ResourceNotFoundException

logger = logging.getLogger(__name__)


def locate_file(path_to_module: str, filename: str) -> str:
    """Tries to locate the file in *module path*.  Starts the search in
    current directory and goes up in directory structure until file is
    found or module namespace is left.

    Args:

        path_to_module (str): directory path, ususally just pass in
                              ``__file__`` built-in

        filename (str): file to look for

    FIXME martin.slouf -- now it only checks 3 levels up, instead of end of
    module namespace.

    """

    assert path_to_module is not None
    assert filename is not None

    path = os.path.dirname(os.path.abspath(path_to_module))
    for i in range(0, 4):
        path2 = path
        for j in range(0, i):
            path2 = os.path.join(path2, "..")
        path3 = os.path.join(path2, filename)
        logger.debug("trying path %s", path3)
        if os.access(path3, os.R_OK):
            logger.debug("file found: %s", path3)
            return path3
    raise ResourceNotFoundException(path_to_module=path_to_module,
                                    filename=filename)


def chunks(col: collections.Iterable, chunk_size: int):
    """Yield successive n-sized chunks from iterable.

    Thanks to: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python

    Args:

        col (collections.Iterable): collection to be chunked

        chunk_size (int): chunk size

    Returns:

        types.GeneratorType: generator over collection of chunks
                             (collection of original elements split into
                             several smaller collections of *chunk_size*
                             length)

    """
    for i in range(0, len(col), chunk_size):
        yield col[i:i + chunk_size]


class Printable(object):

    """Tries to pretty print object properties into a unicode string.

    Suitable for multi-inheritance, see :py:class:`summer.model.Domain`.

    """

    def __str__(self):
        """Return printable object string representation in unicode."""
        tmp = "%s [" % (self.__class__.__name__,)
        for (key, val) in self.__dict__.items():
            tmp += "%s: %s, " % (key, val)
        if len(self.__dict__) > 0:
            tmp = tmp[:-2]
        tmp += "]"
        return tmp

    def __bytes__(self):
        """Return printable object representation in platform specific encoding."""
        encoding = sys.getdefaultencoding()
        return str(self).encode(encoding)

    def __repr__(self):
        return self.__str__()


class FileReader(object):

    """Simple & handy class for reading text file line by line with specified
    encoding.  Converts line read to unicode.  Counts line read.  Does no
    file manipulation (opening, closing) except for reading.  If used, you
    should delegate all reading to this simple class.

    """

    def __init__(self, fin: io.IOBase, enc: str):
        """Creates the :py:class:`FileReader` instance.

        Args:

            fin (io.IOBase): file-like object to be read

            enc (str): file encoding
        """
        self.fin = fin
        self.enc = enc
        self.counter = 0

    def readline(self) -> str:
        """Read single line from a file.

        Returns:

            str: line as unicode string.
        """
        line = self.fin.readline()
        unicode_line = line.decode(self.enc)
        self.counter += 1
        return unicode_line


class ThreadSafeCounter (object):

    """Thread safe counter."""

    def __init__(self, initial_value=0):
        """Creates :py:class:`ThreadSafeCounter` instance.

        Args:

            initial_value (int): initial value

        """
        self.lock = threading.Lock()
        self.counter = initial_value

    def inc(self) -> int:
        """Increase counter by 1 and return new value."""
        with self.lock:
            self.counter += 1
            return self.counter

    def dec(self) -> int:
        """Decrease counter by 1 and return new value."""
        with self.lock:
            self.counter -= 1
            return self.counter

    def get(self) -> int:
        with self.lock:
            return self.counter


class IdGenerator(object):

    """Thread safe id generator."""

    def __init__(self):
        self.counter = ThreadSafeCounter(0)

    def gen_id(self) -> int:
        """Generates new id.

        Returns:

            int: new id

        """
        tmp = self.counter.inc()
        logger.info("new id generated %d", tmp)
        return tmp
