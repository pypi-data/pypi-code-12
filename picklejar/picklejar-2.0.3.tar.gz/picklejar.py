# coding=utf-8
"""PickleJar is a python module that allows you to work with multiple pickles while reading/writing 
them to a single file/jar.
"""
# Copyright (C) 2015 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import os
import dill


class Jar(object):
    """A file containing multiple pickle objects

    :param filepath: Path to the file
    :param always_list: Ensure that Jars with single pickle return as a list
    :return: Jar object
    """
    def __init__(self, filepath, always_list=False):
        self.jar = os.path.abspath(os.path.expanduser(filepath))
        self.always_list = always_list

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return None

    def exists(self):
        """Does the Jar exist

        :return: True or False
        """
        return os.path.exists(self.jar)

    def remove(self):
        """Remove the current jar file if it exists

        :return: True
        """
        if self.__exists():
            os.remove(self.jar)
        return True

    def load(self, always_list=False):
        """Loads all the pickles out of the file/jar

        :param always_list: Ensure that Jars with single pickle return as a list
        :return: List of de-pickled objects
        :raises: IOError if jar file doesn't exist
        """
        items = list()
        if self.__exists() is False:
            raise IOError('File does not exist: ' + self.jar)
        with open(self.jar, 'rb') as jar:
            while True:
                try:
                    items.append(dill.load(jar))
                except EOFError:
                    break
        if len(items) == 1:
            if self.always_list or always_list:
                return items
            else:
                return items[0]
        else:
            return items

    def dump(self, items, newjar=False, collapse=False):
        """Write a Pickle to the file/jar.

        :param items: Item or list of items to pickle
        :param newjar: Start a new jar
        :param collapse: If items is a list write list as single pickle
        :return: True on file write
        """
        if newjar:
            writemode = 'wb'
        else:
            writemode = 'ab'
        with open(self.jar, mode=writemode) as jar:
            if collapse:
                dill.dump(items, jar, dill.HIGHEST_PROTOCOL)
            else:
                if type(items) is list:
                    for item in items:
                        dill.dump(item, jar, dill.HIGHEST_PROTOCOL)
                else:
                    dill.dump(items, jar, dill.HIGHEST_PROTOCOL)
        return True

    # Protecting internal calls so picklejar can be subclassed
    __exists = exists
    __remove = remove
    __load = load
    __dump = dump

