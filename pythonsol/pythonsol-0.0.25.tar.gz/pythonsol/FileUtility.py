"""
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (C) 2013/2014/2015 Laurent Champagnac
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
# ===============================================================================
"""

# Import
import logging

import os
import codecs

from pythonsol.SolBase import SolBase


SolBase.logging_init()
logger = logging.getLogger("FileUtility")


class FileUtility(object):
    """
    Class description
    Open doc : http://docs.python.org/py3k/library/functions.html#open
    Encoding doc : http://docs.python.org/py3k/library/locale.html#locale.getpreferredencoding
    Python 3 is internally unicode for "str" type.
    """

    def __init__(self):
        """
        Constructor.
        :return: Nothing.
        """

    @staticmethod
    def is_path_exist(path_name):
        """
        Check if a path (file or dir) name exist.
        :param path_name: Path name.
        :return: Return true (exist), false (do not exist, or invalid file name)
        """

        # Check
        if path_name is None:
            logger.error("is_path_exist : file_name is None")
            return False
        elif not isinstance(path_name, str):
            logger.error("is_path_exist : path_name not a str, className=%s", SolBase.get_classname(path_name))
            return False

        # Go
        return os.path.exists(path_name)

    @staticmethod
    def is_file_exist(file_name):
        """
        Check if file name exist.
        :param file_name: File name.
        :return: Return true (exist), false (do not exist, or invalid file name)
        """

        # Check
        if file_name is None:
            logger.error("is_file_exist : file_name is None")
            return False
        elif not isinstance(file_name, str):
            logger.error("is_file_exist : file_name not a str, className=%s", SolBase.get_classname(file_name))
            return False

        # Go
        return os.path.isfile(file_name)

    @staticmethod
    def is_dir_exist(dir_name):
        """
        Check if dir name exist.
        :param dir_name: Directory name.
        :return: Return true (exist), false (do not exist, or invalid file name)
        """

        # Check
        if dir_name is None:
            logger.error("is_dir_exist : file_name is None")
            return False
        elif not isinstance(dir_name, str):
            logger.error("is_dir_exist : file_name not a str, className=%s", SolBase.get_classname(dir_name))
            return False

        # Go
        return os.path.isdir(dir_name)

    @staticmethod
    def get_file_size(file_name):
        """
        Return a file size in bytes.
        :param file_name: File name.
        :return: An integer, gt-eq 0 if file exist, lt 0 if error.
        """
        if not FileUtility.is_file_exist(file_name):
            return -1
        else:
            return os.path.getsize(file_name)

    @classmethod
    def get_current_dir(cls):
        """
        Return the current directory.
        :return: A String
        """

        return os.getcwd()

    @classmethod
    def split_path(cls, path):
        """
        Split path, returning a list.
        :param path: A path.
        :return: A list of path component.
        """
        return path.split(SolBase.get_pathseparator())

    @staticmethod
    def file_to_byte_buffer(file_name):
        """
        Load a file toward a binary buffer.
        :param file_name: File name.
        :return: Return the binary buffer or None in case of error.
        """

        # Check
        if not FileUtility.is_file_exist(file_name):
            logger.error("file_to_byte_buffer : file_name not exist, file_name=%s", file_name)
            return None

        # Go
        rd = None
        try:
            # Open (binary : open return a io.BufferedReader)
            rd = open(file_name, "rb")

            # Preallocate buffer (faster)
            binbuf = bytearray(FileUtility.get_file_size(file_name))

            # Read everything
            # noinspection PyArgumentList
            rd.readinto(binbuf)

            # Return
            return binbuf
        except IOError as e:
            # Exception...
            logger.error("file_to_byte_buffer : IOError, ex=%s", SolBase.extostr(e))
            return None
        except Exception as e:
            logger.error("file_to_byte_buffer : Exception, ex=%s", SolBase.extostr(e))
            return None
        finally:
            # Close if not None...
            if rd:
                rd.close()

    @staticmethod
    def file_to_textbuffer(file_name, encoding):
        """
        Load a file toward a text buffer (UTF-8), using the specify encoding while reading.
        CAUTION : This will read the whole file IN MEMORY.
        :param file_name: File name.
        :param encoding: Encoding to user.
        :return: A text buffer or None in case of error.
        """

        # Check
        if not FileUtility.is_file_exist(file_name):
            logger.error("file_to_textbuffer : file_name not exist, file_name=%s", file_name)
            return None

        # Go
        rd = None
        try:
            # Open (text : open return a io.BufferedReader)
            rd = codecs.open(file_name, "rt", encoding, "strict", -1)

            # Read everything
            return rd.read()
        except IOError as e:
            # Exception...
            logger.error("file_to_byte_buffer : IOError, ex=%s", SolBase.extostr(e))
            return None
        except Exception as e:
            logger.error("file_to_byte_buffer : Exception, ex=%s", SolBase.extostr(e))
            return None
        finally:
            # Close if not None...
            if rd:
                rd.close()

    @staticmethod
    def append_binary_tofile(file_name, bin_buf):
        """
        Write to the specified filename, the provided binary buffer.
        Create the file if required.
        :param file_name:  File name.
        :param bin_buf: Binary buffer to write.
        :return: The number of bytes written or lt 0 if error.
        """

        # Go
        rd = None
        try:
            # Open (text : open return a io.BufferedReader)
            rd = open(file_name, "ab+")

            # Read everything
            return rd.write(bin_buf)
        except IOError as e:
            # Exception...
            logger.error("append_binary_tofile : IOError, ex=%s", SolBase.extostr(e))
            return -1
        except Exception as e:
            logger.error("append_binary_tofile : Exception, ex=%s", SolBase.extostr(e))
            return -1
        finally:
            # Close if not None...
            if rd:
                rd.close()

    @staticmethod
    def append_text_tofile(file_name, text_buffer, encoding, overwrite=False):
        """
        Write to the specified filename, the provided binary buffer
        Create the file if required.
        :param file_name:  File name.
        :param text_buffer: Text buffer to write.
        :param encoding: The encoding to user.
        :param overwrite: If true, file is overwritten.
        :return: The number of bytes written or lt 0 if error.
        """

        # Go
        rd = None
        try:
            # Open (text : open return a io.BufferedReader)
            if not overwrite:
                rd = codecs.open(file_name, "at+", encoding, "strict", -1)
            else:
                rd = codecs.open(file_name, "wt", encoding, "strict", -1)

            # Read everything
            # CAUTION : 2.7 return None :(
            return rd.write(text_buffer)
        except IOError as e:
            # Exception...
            logger.error("append_text_tofile : IOError, ex=%s", SolBase.extostr(e))
            return -1
        except Exception as e:
            logger.error("append_text_tofile : Exception, ex=%s", SolBase.extostr(e))
            return -1
        finally:
            # Close if not None...
            if rd:
                rd.close()
