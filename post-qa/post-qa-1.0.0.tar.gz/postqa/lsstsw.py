"""Tools for working with lsstsw installations."""

from __future__ import (division, absolute_import, print_function,
                        unicode_literals)
from builtins import *  # NOQA
from future.standard_library import install_aliases
install_aliases()  # NOQA

import os
import git

from .pkgdata import Manifest


class Lsstsw(object):
    """An lsstsw installation.

    Parameters
    ----------
    dirname : `str`
        Path of an ``lsstsw`` directory.
    """
    def __init__(self, dirname):
        super(Lsstsw, self).__init__()
        self._dirname = dirname

    @property
    def manifest_path(self):
        """Path of the manifest.txt file."""
        return os.path.join(self._dirname, 'build', 'manifest.txt')

    def package_repo_path(self, package_name):
        """Path to a EUPS package repository in lsstsw/build."""
        return os.path.join(self._dirname, 'build', package_name)

    def package_branch(self, package_name):
        """Git branch of an EUPS package cloned in lsstsw/build."""
        repo = git.Repo(self.package_repo_path(package_name))
        return repo.active_branch.name

    @property
    def json(self):
        """Job JSON document, as a `dict` containing a `packages` field."""
        with open(self.manifest_path, encoding='utf-8') as f:
            manifest = Manifest(f)
        job_json = manifest.json

        # Insert git branch information
        for pkg_doc in job_json['packages']:
            pkg_doc['git_branch'] = self.package_branch(pkg_doc['name'])

        return job_json
