# -*- coding: utf-8 -*-


# Copyright (c) 2016  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Petr Šabata <contyk@redhat.com>


class ModuleContent(object):
    """Base class for module content."""

    def __init__(self):
        """Creates a new ModuleContent instance."""
        self.packages = dict()

    @property
    def packages(self):
        """A dictionary property representing the package list.

        Keys (strings) are package names, values (dictionaries or None) are
        implementation specific extra data.
        """
        return self._packages

    @packages.setter
    def packages(self, d):
        if d and not isinstance(d, dict):
            raise TypeError("packages requires a dict")
        self._packages = d

    def add_package(self, p, rationale=""):
        """Adds a package to the package list.

        :param str p: Package name
        :param str rationale: Rationale for this package
        :raises TypeError: If the supplied data type is not valid
        """
        if not isinstance(rationale, str):
            raise TypeError("rationale must be a string")
        pkgs = self._packages
        pkgs[p] = dict()
        pkgs[p]["rationale"] = rationale
        self.packages = pkgs

    update_package = add_package

    def del_package(self, p):
        """Deletes the supplied package from the package list.

        :param str p: Package name
        """
        if p in self._packages:
            del self._packages[p]

    def clear_packages(self):
        """Clears the package list."""
        self._packages = dict()
