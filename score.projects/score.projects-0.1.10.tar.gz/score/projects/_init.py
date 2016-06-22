# Copyright © 2015,2016 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

from score.init import ConfiguredModule, parse_bool
from .project import Project
import os
from score.cli.conf import rootdir, name2file, add as addconf, get_origin
import configparser
import shutil


defaults = {
}


def init(confdict={}):
    """
    Initializes this module acoording to :ref:`our module initialization
    guidelines <module_initialization>`.
    """
    conf = defaults.copy()
    conf.update(confdict)
    return ConfiguredProjectsModule()


class ConfiguredProjectsModule(ConfiguredModule):
    """
    This module's :class:`score.init.ConfiguredModule`. It also acts as an
    iterator, yielding all known projects:

    .. code-block:: python

        >>> import score.projects
        >>> for project in score.projects.init():
        ...     print(project.name)
        ...
    """

    def __init__(self):
        import score.projects
        super().__init__(score.projects)

    def get(self, name):
        """
        Returns the project with given *name*, raising a ProjectNotFound, if no
        such project was encountered.

        The *name* can also ba an instance of :class:`Project`, in which case it
        will be returned immediately. This makes the rest of the API quite
        convenient: it does not matter, whether you pass a :class:`Project`
        object, or a project name.
        """
        if isinstance(name, Project):
            return name
        try:
            return next(p for p in self if p.name == name)
        except StopIteration:
            raise ProjectNotFound(name)

    def relocate(self, project, folder):
        """
        Moves the code folder of given *project* to the specified *folder*.
        """
        project = self.get(project)
        shutil.move(project.folder, folder)
        configurations = name2file(include_global=False, venv=project.venvdir)
        for name, path in configurations.items():
            path = get_origin(path)
            if not path.startswith(project.folder):
                continue
            relpath = os.path.relpath(path, project.folder)
            newpath = os.path.join(folder, relpath)
            addconf(name, newpath, venv=project.venvdir)
        project.folder = folder
        project.install()
        settings = self._read_conf()
        settings[project.name] = {'folder': folder}
        self._write_conf(settings)
        return project

    def rename(self, project, newname):
        """
        Changes the name of a given *project* to *newname*. The *project* can be
        anything accepted by :meth:`get`.

        .. note::

            Since the folder path of a project's virtual environment depends on
            its name, the function will also delete the project's old virtualenv
            and create a new one.
        """
        project = self.get(project)
        oldname = project.name
        try:
            shutil.rmtree(project.venvdir)
        except FileNotFoundError:
            pass
        project.name = newname
        settings = self._read_conf()
        try:
            site_packages = parse_bool(settings[oldname]['site_packages'])
        except:
            site_packages = False
        project.recreate_venv(site_packages=site_packages)
        del settings[oldname]
        settings[newname] = {'folder': project.folder}
        self._write_conf(settings)

    def delete(self, project):
        """
        Deletes the virtualenv of given *project*. The *project* can be anything
        accepted by :meth:`get`.
        """
        project = self.get(project)
        try:
            shutil.rmtree(project.venvdir)
        except FileNotFoundError:
            pass
        settings = self._read_conf()
        del settings[project.name]
        self._write_conf(settings)
        return project

    def register(self, name, folder, site_packages=False):
        """
        Registers a new project with given *name* and associates it with the
        given *folder*.
        """
        if name in self.all():
            raise ValueError('Project "%s" already exists' % name)
        project = Project(self, name, folder)
        project.recreate_venv(site_packages=site_packages)
        settings = self._read_conf()
        settings[name] = {
            'folder': folder,
            'site_packages': str(site_packages)
        }
        self._write_conf(settings)
        return project

    def all(self):
        """
        Returns a `dict` mapping project names to :class:`Project` objects.
        """
        return dict((p.name, p) for p in self)

    def __iter__(self):
        settings = self._read_conf()
        for section in settings:
            if section == 'DEFAULT':
                continue
            folder = settings[section]['folder']
            yield(Project(self, section, folder))

    __getitem__ = get

    def _read_conf(self):
        root = os.path.join(rootdir(global_=True), 'projects')
        settings = configparser.ConfigParser()
        settings.read(os.path.join(root, 'list.conf'))
        return settings

    def _write_conf(self, settings):
        root = os.path.join(rootdir(global_=True), 'projects')
        file = os.path.join(root, 'list.conf')
        settings.write(open(file, 'w'))


class ProjectNotFound(Exception):
    """
    Raised when a requested project could not be found.
    """
    pass
