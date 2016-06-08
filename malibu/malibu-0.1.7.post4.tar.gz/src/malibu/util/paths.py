# -*- coding: utf-8 -*-
from os.path import dirname, expanduser, normpath, realpath


def expand_path(path):
    """ Expands a path to it's full, non-relative, fully
        resolved counterpart.
    """

    return realpath(normpath(expanduser(path)))


def get_path_base(path):
    """ Returns the parent of the specified path. Fully resolves
        the path before getting the basename. Uses expand_path()
        for expansion.
    """

    return dirname(expand_path(path))
