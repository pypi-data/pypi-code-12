#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import platform
import sys
import site
import os

__version__ = "0.0.1"
__short_description__ = "Cross Operation System Compatible Library."
__license__ = "MIT"
__author__ = "Sanhe Hu"

WINDOWS, MACOS, LINUX = False, False, False
_system = platform.system()
if _system == "Windows":
    WINDOWS = True
    SP_PATH = site.getsitepackages()[1]
    PROGRAM_FILES_64 = r"C:\Program Files"
    PROGRAM_FILES_32 = r"C:\Program Files (x86)"
elif _system == "Darwin":
    MACOS = True
    SP_PATH = site.getsitepackages()[0]
elif _system == "Linux":
    LINUX = True
    SP_PATH = site.getsitepackages()[0]

USER_PATH = os.path.expanduser('~')