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


from modulemd.content import ModuleContent

class ModuleRPMs(ModuleContent):
    """A ModuleContent subclass for RPM-type module content."""

    def __init__(self):
        """Creates a new ModuleRPMs instance."""
        self._dependencies = False
        self._api = set()
        self._packages = dict()
        self._filter = set()

    def add_package(self, p, rationale="", commit=None, repository=None, cache=None, arches=None, multilib=None):
        """Adds a package to the package list.

        :param str p: Package name
        :param str rationale: Rationale for this package
        :param commit: Commit hash pointing to the package sources
        :param repository: Path to the VCS repository with the sources
        :param cache: Path to the lookaside cache
        :param arches: Architectures the package is available on
        :param multilib: Architectures the package is installed as multilib on
        :type commit: str or None
        :type repository: str or None
        :type cache: str or None
        :type arches: list or None
        :type multilib: list or None
        :raises TypeError: If the supplied data type is invalid
        """
        pkgs = self._packages
        pkgs[p] = dict()
        pkgs[p]["rationale"] = rationale
        if commit:
            if not isinstance(commit, str):
                raise TypeError("commit must be a string")
            pkgs[p]["commit"] = commit
        if repository:
            if not isinstance(repository, str):
                raise TypeError("repository must be a string")
            pkgs[p]["repository"] = repository
        if cache:
            if not isinstance(cache, str):
                raise TypeError("cache must be a string")
            pkgs[p]["cache"] = cache
        if arches:
            if not isinstance(arches, list):
                raise TypeError("arches requires a list")
            pkgs[p]["arches"] = arches
        if multilib:
            if not isinstance(multilib, list):
                raise TypeError("multilib requires a list")
            pkgs[p]["multilib"] = multilib
        self.packages = pkgs

    update_package = add_package

    @property
    def dependencies(self):
        """A boolean property indicating whether the packages' dependencies
        should be included within the module or not.
        """
        return self._dependencies

    @dependencies.setter
    def dependencies(self, b):
        self._dependencies = bool(b)

    @property
    def filter(self):
        """A list of binary package names to be filtered out
        """
        return self._filter

    @filter.setter
    def filter(self, ss):
        if not isinstance(ss, set):
            raise TypeError("filter requires a set")
        self._filter = ss

    def add_filter(self, s):
        """Adds a string to the set of filters

        :param str s: RPM binary package name
        """
        self._filter.add(str(s))

    update_filter = add_filter

    def del_filter(self, s):
        """Remove the supplied binary package name from the set of filters.

        :param str s: RPM binary package name
        """
        self._filter.discard(str(s))

    def clear_filter(self):
        """Clears the RPM package name filter set."""
        self._filter.clear()

    @property
    def api(self):
        """A set of RPM binary package names representing the external,
        supported API of the module.
        """
        return self._api

    @api.setter
    def api(self, ss):
        if not isinstance(ss, set):
            raise TypeError("api requires a set")
        self._api = ss

    def add_api(self, s):
        """Adds an RPM binary package API symbol to the set.

        :param str s: RPM binary package name
        """
        self._api.add(str(s))

    update_api = add_api

    def del_api(self, s):
        """Remove the supplied RPM binary package API symbol from the set.

        :param str s: RPM binary package name
        """
        self._api.discard(str(s))

    def clear_api(self):
        """Clears the RPM package name API symbol set."""
        self._api.clear()
