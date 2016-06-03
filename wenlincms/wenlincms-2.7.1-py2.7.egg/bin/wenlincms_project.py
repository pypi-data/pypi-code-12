#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import os
from distutils.dir_util import copy_tree
from optparse import OptionParser

from wenlincms.utils.importing import path_for_import


def create_project():
    """
    复制 project_template 到当前目录
    """

    parser = OptionParser(usage="usage: %prog [options] project_name")
    parser.add_option("-a", "--alternate", dest="alt", metavar="PACKAGE",
                      help="Alternate package to use, containing a project_template")
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("project_name must be specified")
    project_name = args[0]
    if project_name.startswith("-"):
        parser.error("project_name cannot start with '-'")
    project_path = os.path.join(os.getcwd(), project_name)

    # Ensure the given directory name doesn't clash with an existing
    # Python package/module.
    try:
        __import__(project_name)
    except ImportError:
        pass
    else:
        parser.error("'%s' conflicts with the name of an existing "
                     "Python module and cannot be used as a project "
                     "name. Please try another name." % project_name)

    # Create the list of packages to build from - at this stage it
    # should only be one or two names, wenlincms plus an alternate
    # package.
    packages = ["wenlincms"]
    if options.alt:
        packages.append(options.alt)
    for package_name in packages:
        try:
            __import__(package_name)
        except ImportError:
            parser.error("Could not import package '%s'" % package_name)

    # Build the project up copying over the project_template from
    # each of the packages. An alternate package will overwrite
    # files from wenlincms.
    for package_name in packages:
        package_path = path_for_import(package_name)
        copy_tree(os.path.join(package_path, "project_template"), project_path)

    for (root, dirs, files) in os.walk(project_path, False):
        for f in files:
            try:
                if f.endswith(".pyc"):
                    os.remove(os.path.join(root, f))
            except:
                pass


if __name__ == "__main__":
    create_project()
