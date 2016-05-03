# -*- coding: utf-8 -*-

import platform
import sys

from .decorators import posix_only


def is_64bits():
    return sys.maxsize > 2**32


def is_32bits():
    return is_64bits() is False


def os_name():
    return platform.platform()


@posix_only
def dist():
    return " ".join(platform.dist())
