# This file is part of the Online Services test tools
#
# Copyright 2014 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 3, as published by the
# Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranties of MERCHANTABILITY,
# SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import os

from olstests import matchers


class Walker(object):

    def __init__(self, root, file_matcher=None, dir_matcher=None,
                 file_handler=None, dir_handler=None,
                 sort_key=None):
        self.root = root
        if file_matcher is None:
            # Match everything
            file_matcher = matchers.NameMatcher(includes=[r'.*'])
        if dir_matcher is None:
            # Match everything
            dir_matcher = matchers.NameMatcher(includes=[r'.*'])
        self.file_matcher = file_matcher
        self.dir_matcher = dir_matcher
        self.file_handler = file_handler
        self.dir_handler = dir_handler
        self.sort_key = sort_key

    def SubWalker(self, root=None, file_matcher=None, dir_matcher=None,
                  file_handler=None, dir_handler=None,
                  sort_key=None):
        """Creates a new walker overriding walk policy.

        :param root: Optional. A new root to redirect the tree traversal.

        :param file_matcher: Optional. A new matcher to filter files.

        :param dir_matcher: Optional. A new matcher to filter directories.

        :param file_handler: A callable processing the file name. The signature
            is (walker, dir_from_root, file base name), the returned value is
            yielded by iter().

        :param dir_handler: A callable processing the dir.  The signature is
             (walker, dir_from_root), the returned values are yielded one by
             one by iter().

        :return: A new walker with the new policy, leaving the original walker
            untouched.
        """
        if root is None:
            root = self.root
        if file_matcher is None:
            file_matcher = self.file_matcher
        if dir_matcher is None:
            dir_matcher = self.dir_matcher
        if file_handler is None:
            file_handler = self.file_handler
        if dir_handler is None:
            dir_handler = self.dir_handler
        if sort_key is None:
            sort_key = self.sort_key
        # Create a clone copying the attributes that defines the current policy
        # if no specific values are provided by the caller.
        return self.__class__(root=root,
                              file_matcher=file_matcher,
                              dir_matcher=dir_matcher,
                              file_handler=file_handler,
                              dir_handler=dir_handler,
                              sort_key=sort_key)

    def join_root(self, *parts):
        """Return the walker root joined with a list of path parts.

        :param parts: Any number of path parts (including 0).

        This provides a bridge between internal needs for paths including root
        while supporting relative paths in the API. This allows the callers to
        keep clean paths from a known starting root.
        """
        return os.path.join(self.root, *parts)

    def sort_names(self, names):
        """Sort the received names."""
        if self.sort_key is None:
            return names
        return sorted(names, key=self.sort_key)

    def names(self, dir_path):
        """The list of names found in the given directory.

        :param dir_path: The path, relative to root, to list.
        """
        full_path = self.join_root(dir_path)
        if full_path == '':
            # Allowing '' to mean '.' makes for simpler code
            full_path = '.'
        return os.listdir(full_path)

    def iter(self, dir_path, names=None):
        """Iter all items in the file system from the walker's root.

        This iterates the file system starting at dir_path under root, passing
        the matching files and dirs to their respective handlers and yielding
        the results.

        :param dir_path: The path, relative to root, to iter.

        :param names: The names to iterate on in 'dir_path'. If None, all the
            existing names in 'dir_path' are iterated.
        """
        if names is None:
            names = self.sort_names(self.names(dir_path))
        for name in names:
            rel_path = os.path.join(dir_path, name)
            if self.file_handler is not None \
                    and os.path.isfile(self.join_root(rel_path)) \
                    and self.file_matcher.matches(name):
                # If the file matches, yield the result
                yield self.file_handler(self, dir_path, name)
            elif self.dir_handler is not None \
                    and os.path.isdir(self.join_root(rel_path)) \
                    and self.dir_matcher.matches(name):
                # If the dir matches, yield all results
                for name_in_dir in self.dir_handler(self, rel_path):
                    yield name_in_dir
