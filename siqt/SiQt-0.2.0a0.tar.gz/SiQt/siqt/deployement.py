# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import sys
import os
import re

def _resource_path(relative):
    """ Normalisation of the ressource path for PyInstaller """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    else:
        basedir = os.path.split(os.path.split(__file__)[0])[0]
        return os.path.join(basedir, relative)


